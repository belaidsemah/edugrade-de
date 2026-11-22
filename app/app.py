import os, json, logging, uuid, datetime
import jwt, psycopg2
from flask import Flask, request, jsonify, g
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
JWT_SECRET = os.environ["JWT_SECRET"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

log = logging.getLogger("edugrade")
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(_h)
log.setLevel(logging.INFO)

def event(name, level=logging.INFO, **kw):
    log.log(level, json.dumps({
        "ts": datetime.datetime.utcnow().isoformat(), "event": name,
        "request_id": getattr(g, "rid", None), "user_id": getattr(g, "uid", None),
        "ip": request.remote_addr, "path": request.path, **kw}))

def db():
    return psycopg2.connect(host=os.getenv("DB_HOST", "db"), dbname="edugrade",
                            user="edugrade", password=DB_PASSWORD)

@app.before_request
def start():
    g.rid = str(uuid.uuid4())
    g.uid = None

@app.after_request
def headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "DENY"
    r.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    r.headers["Cache-Control"] = "no-store"
    r.headers["X-Request-ID"] = g.get("rid", "")
    return r

def current_user():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        u = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        g.uid = u["sub"]
        return u
    except Exception:
        return None

def can_access(u, student_id):
    return u["role"] in ("teacher", "admin") or u["sub"] == str(student_id)

@app.post("/register")
def register():
    d = request.get_json()
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO users (email,password,role) VALUES (%s,%s,'student')",
                (d["email"], generate_password_hash(d["password"])))
    conn.commit()
    return jsonify(ok=True), 201

@app.post("/login")
def login():
    d = request.get_json()
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT id, role, password FROM users WHERE email=%s", (d["email"],))
    row = cur.fetchone()
    if not row or not check_password_hash(row[2], d["password"]):
        event("login_failed", logging.WARNING)
        return jsonify(error="invalid"), 401
    token = jwt.encode({"sub": str(row[0]), "role": row[1],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        JWT_SECRET, algorithm="HS256")
    return jsonify(token=token)

@app.get("/grades/<int:student_id>")
def grades(student_id):
    u = current_user()
    if not u:
        return jsonify(error="unauthorized"), 401
    if not can_access(u, student_id):
        event("access_denied", logging.WARNING, target=student_id)
        return jsonify(error="forbidden"), 403
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT course, grade, comment FROM grades WHERE student_id=%s", (student_id,))
    rows = [[c, float(gr), m] for c, gr, m in cur.fetchall()]
    return jsonify(student_id=student_id, grades=rows)

@app.post("/grades")
def add_grade():
    u = current_user()
    if not u:
        return jsonify(error="unauthorized"), 401
    if u["role"] not in ("teacher", "admin"):
        event("access_denied", logging.WARNING, action="add_grade")
        return jsonify(error="forbidden"), 403
    d = request.get_json()
    conn = db(); cur = conn.cursor()
    cur.execute("INSERT INTO grades (student_id,course,grade,comment) VALUES (%s,%s,%s,%s)",
                (d["student_id"], d["course"], d["grade"], d.get("comment", "")))
    conn.commit()
    return jsonify(ok=True), 201

@app.get("/bulletin/<int:student_id>")
def bulletin(student_id):
    u = current_user()
    if not u:
        return jsonify(error="unauthorized"), 401
    if not can_access(u, student_id):
        event("access_denied", logging.WARNING, target=student_id)
        return jsonify(error="forbidden"), 403
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT course, grade, comment FROM grades WHERE student_id=%s", (student_id,))
    rows = "".join(f"<tr><td>{escape(c)}</td><td>{gr}</td><td>{escape(m)}</td></tr>"
                   for c, gr, m in cur.fetchall())
    return f"<h1>Bulletin {student_id}</h1><table>{rows}</table>"

@app.get("/students/search")
def search():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return jsonify(error="forbidden"), 403
    conn = db(); cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE email LIKE %s",
                (f"%{request.args.get('q', '')}%",))
    return jsonify(results=cur.fetchall())

@app.get("/health")
def health():
    return jsonify(status="ok")
