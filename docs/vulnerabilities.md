# Failles initiales (AVANT correction)

| ID | Faille | OWASP Top 10 (édition en vigueur: à vérifier) | Emplacement | Cause | Impact | Preuve (capture) | Correctif | Preuve post-fix |
|---|---|---|---|---|---|---|---|---|
| V1 | IDOR | Broken Access Control | /grades/<id>, /bulletin/<id> | pas de contrôle propriétaire | lecture notes d'autrui | A2 | can_access() | A2b |
| V2 | SQLi | Injection | /login, /students/search | f-string SQL | bypass auth, dump | A3, A4 | requêtes paramétrées | A3b |
| V3 | Dépendances vulnérables | Vulnerable and Outdated Components | requirements.txt | versions anciennes | CVE | D2 | upgrade | D3 |
| V4 | Secret hardcodé | Cryptographic Failures / Misconfig | app.py | secret en dur | forge de JWT | D1 | variables d'env | E4 |
| V5 | Misconfiguration | Security Misconfiguration | debug=True, root | défauts | exécution via console debug | A7 | debug off, non-root | C1 |
| V6 | Élévation de rôle | Broken Access Control | /register, POST /grades | rôle du body, pas de check | student -> admin/teacher | A5 | rôle forcé + check | A5b |
| V7 | XSS stocké | Injection | /bulletin | HTML non échappé | vol de session | A6 | escape() | A6b |
