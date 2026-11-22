from werkzeug.security import generate_password_hash as g
users = [("admin@edugrade.test","admin123","admin"),("prof@edugrade.test","prof123","teacher"),
         ("alice@edugrade.test","alice123","student"),("bob@edugrade.test","bob123","student")]
sql = """CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'student');
CREATE TABLE grades (id SERIAL PRIMARY KEY, student_id INT REFERENCES users(id), course TEXT, grade NUMERIC(4,2), comment TEXT);
"""
for e, p, r in users:
    sql += f"INSERT INTO users (email,password,role) VALUES ('{e}','{g(p)}','{r}');\n"
sql += """INSERT INTO grades (student_id,course,grade,comment) VALUES
 (3,'Réseaux',15.5,'Bon travail'),(3,'Sécurité',17,'Excellent'),(4,'Réseaux',9,'Peut mieux faire'),(4,'Sécurité',11,'Moyen');
"""
open("db/init.sql", "w").write(sql)
print("db/init.sql genere")
