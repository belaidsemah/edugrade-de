CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'student');
CREATE TABLE grades (id SERIAL PRIMARY KEY, student_id INT REFERENCES users(id), course TEXT, grade NUMERIC(4,2), comment TEXT);
INSERT INTO users (email,password,role) VALUES ('admin@edugrade.test','scrypt:32768:8:1$Poc94hIJ0GaBxbXC$53ab3bdfa96f40ba615a3fdb7836522506ded532d14ce464b8fa789f1481710344f14e475ec3de565efe7c8da9642a8460b79b5c518659e71165808a3bcf72a6','admin');
INSERT INTO users (email,password,role) VALUES ('prof@edugrade.test','scrypt:32768:8:1$hsVnSRxqZ1GZL1vM$181c99273eebf10196d96e22308c2a16d77101d3d54158364c341ff6c0dae14bbfb842d8ae77e73e2db4d89afe3d125d1ce95f663395d836373147f949e4364e','teacher');
INSERT INTO users (email,password,role) VALUES ('alice@edugrade.test','scrypt:32768:8:1$W0306KlJOA7Ux7gN$2470ed1d5bac4615e9131da4d64da690c8cbec871ac1c7af3aa9482d9b5b98949fa3a7f0357922e95c92559898be4bbe8ea681b38362ed06ab9a897cf54912cc','student');
INSERT INTO users (email,password,role) VALUES ('bob@edugrade.test','scrypt:32768:8:1$Kmggywlwtd8Vkxzv$55c0394dec3e1e8cfa48ace8fdabb86a31346312a7e0feee727581a2e8ed6e79da78756382046ce793d3f217d4af8bfd680900db970d2b2094e5fb8027ad16f7','student');
INSERT INTO grades (student_id,course,grade,comment) VALUES
 (3,'Réseaux',15.5,'Bon travail'),(3,'Sécurité',17,'Excellent'),(4,'Réseaux',9,'Peut mieux faire'),(4,'Sécurité',11,'Moyen');
