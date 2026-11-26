import os, sqlite3, jwt, json, uuid, logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
SECRET_KEY = os.environ.get("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is required")

DB_PATH = os.environ.get("DB_PATH", "/tmp/edugrade_sec.db")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "correlation_id": getattr(g, "correlation_id", "system"),
            "message": record.getMessage(),
            "path": request.path if request else None,
            "remote_addr": request.remote_addr if request else None,
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
app.logger.handlers = [handler]
app.logger.setLevel(logging.INFO)

@app.before_request
def set_correlation_id():
    g.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY, student_id INTEGER, course TEXT, grade REAL)")
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM grades")
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (1, "alice", generate_password_hash("AliceStrong#2026"), "student"))
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (2, "bob", generate_password_hash("BobStrong#2026"), "student"))
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (3, "prof", generate_password_hash("ProfStrong#2026"), "teacher"))
    c.execute("INSERT INTO grades VALUES (1, 1, 'DevSecOps', 18.5), (2, 2, 'DevSecOps', 11.0)")
    conn.commit()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    u = str(data.get("username", ""))
    p = str(data.get("password", ""))
    if "'" in u or "--" in u or "UNION" in u.upper():
        app.logger.warning(f"SECURITY_ALERT: Potential SQLi attempt detected for username={u}")
        return jsonify({"error": "Invalid input"}), 400
    conn = sqlite3.connect(DB_PATH)
    user = conn.execute("SELECT id, username, password, role FROM users WHERE username=?", (u,)).fetchone()
    conn.close()
    if user and check_password_hash(user[2], p):
        token = jwt.encode({"user_id": user[0], "role": user[3]}, SECRET_KEY, algorithm="HS256")
        app.logger.info(f"Successful login user_id={user[0]}")
        return jsonify({"token": token, "role": user[3]}), 200
    app.logger.warning(f"Failed login attempt for username={u}")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/grades/<int:student_id>", methods=["GET"])
def get_grades(student_id):
    auth = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(auth, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401
    if payload.get("role") == "student" and payload.get("user_id") != student_id:
        app.logger.warning(f"SECURITY_ALERT: IDOR blocked user_id={payload.get('user_id')} tried target={student_id}")
        return jsonify({"error": "Forbidden"}), 403
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT course, grade FROM grades WHERE student_id=?", (student_id,)).fetchall()
    conn.close()
    return jsonify({"student_id": student_id, "grades": rows}), 200

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

@app.route("/", methods=["GET"])
def index():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>EduGrade — Portail DevSecOps Sécurisé</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; max-width: 720px; margin: 40px auto; padding: 20px; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
    h1 { color: #38bdf8; margin-top: 0; }
    input, button { padding: 10px; border-radius: 6px; border: 1px solid #475569; margin: 5px 0; width: 100%; box-sizing: border-box; }
    input { background: #0f172a; color: #f8fafc; }
    button { background: #0284c7; color: white; font-weight: bold; cursor: pointer; border: none; }
    button:hover { background: #0369a1; }
    pre { background: #020617; padding: 12px; border-radius: 6px; overflow-x: auto; color: #4ade80; }
    .badge { background: #065f46; color: #6ee7b7; padding: 3px 8px; border-radius: 999px; font-size: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>EduGrade <span class="badge">DevSecOps Hardened</span></h1>
    <p>Portail académique sécurisé — TEK-UP University (ING-5-J-SSIRF)</p>
  </div>

  <div class="card">
    <h3>1. Authentification Sécurisée (Anti-SQLi & JWT)</h3>
    <input id="user" placeholder="Nom d'utilisateur (ex: alice ou payload SQLi)" value="alice">
    <input id="pass" type="password" placeholder="Mot de passe" value="AliceStrong#2026">
    <button onclick="login()">Se connecter (/login)</button>
    <pre id="loginOut">En attente...</pre>
  </div>

  <div class="card">
    <h3>2. Consultation des Notes (Contrôle RBAC / Anti-IDOR)</h3>
    <input id="sid" placeholder="ID Étudiant (ex: 1 ou 2)" value="1">
    <button onclick="getGrades()">Consulter (/api/grades//grades/&lt;id&gt;lt;id/grades/&lt;id&gt;gt;)</button>
    <pre id="gradesOut">En attente...</pre>
  </div>

  <script>
    let token = "";
    async function login() {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: document.getElementById('user').value, password: document.getElementById('pass').value})
      });
      const data = await res.json();
      if (data.token) token = data.token;
      document.getElementById('loginOut').textContent = JSON.stringify(data, null, 2);
    }
    async function getGrades() {
      const id = document.getElementById('sid').value;
      const res = await fetch('/api/grades/' + id, {
        headers: token ? {'Authorization': 'Bearer ' + token} : {}
      });
      const text = await res.text();
      document.getElementById('gradesOut').textContent = 'HTTP ' + res.status + '\\n' + text;
    }
  </script>
</body>
</html>""", 200
