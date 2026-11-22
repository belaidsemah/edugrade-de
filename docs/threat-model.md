# Modèle de menace (STRIDE)
Diagramme: Utilisateur -> (frontière: internet/cluster) -> App Flask -> (frontière: app/DB) -> PostgreSQL

| Composant | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| /login | vol de JWT | SQLi | pas de logs | | brute force | |
| /grades/<id> | | | | IDOR | | |
| POST /grades | | étudiant modifie notes | | | | student -> teacher |
| /bulletin | | XSS stocké | | | | |
| /register | | | | | | role=admin |
| PostgreSQL | | | | dump via SQLi | | |
