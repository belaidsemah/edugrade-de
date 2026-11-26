import os, sqlite3, jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
# FAILLE 1 : Secret codé en dur (Hardcoded Secret)
SECRET_KEY = "edugrade_super_secret_key_123"

def init_db():
    conn = sqlite3.connect("/tmp/edugrade.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY, student_id INTEGER, course TEXT, grade REAL)")
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM grades")
    c.execute("INSERT INTO users VALUES (1, 'alice', 'alice123', 'student'), (2, 'bob', 'bob123', 'student'), (3, 'prof', 'prof123', 'teacher')")
    c.execute("INSERT INTO grades VALUES (1, 1, 'DevSecOps', 18.5), (2, 2, 'DevSecOps', 11.0)")
    conn.commit()
    conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "")
    p = data.get("password", "")
    conn = sqlite3.connect("/tmp/edugrade.db")
    # FAILLE 2 : Injection SQL (SQLi)
    query = f"SELECT id, username, role FROM users WHERE username='{u}' AND password='{p}'"
    user = conn.execute(query).fetchone()
    conn.close()
    if user:
        token = jwt.encode({"user_id": user[0], "role": user[2]}, SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes): token = token.decode()
        return jsonify({"token": token, "role": user[2]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/grades/<int:student_id>", methods=["GET"])
def get_grades(student_id):
    auth = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(auth, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401
    # FAILLE 3 : IDOR (aucune vérification que payload['user_id'] == student_id)
    conn = sqlite3.connect("/tmp/edugrade.db")
    rows = conn.execute("SELECT course, grade FROM grades WHERE student_id=?", (student_id,)).fetchall()
    conn.close()
    return jsonify({"student_id": student_id, "requested_by": payload["user_id"], "grades": rows})

@app.route("/api/admin/promote/<int:user_id>", methods=["POST"])
def promote(user_id):
    # FAILLE 4 : Élévation de privilèges (aucun contrôle de rôle admin/teacher)
    conn = sqlite3.connect("/tmp/edugrade.db")
    conn.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": f"User {user_id} promoted to admin"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
