# Politique de blocage du pipeline

| Gravité / événement | Action | Exception | Échéance |
|---|---|---|---|
| Secret détecté | Blocage | Aucune | Rotation immédiate, puis purge |
| CRITICAL (deps, image, IaC) | Blocage | Aucune | - |
| HIGH | Blocage | Uniquement si aucun correctif upstream; `.trivyignore` commenté (CVE, raison, date, responsable) | 14 jours |
| MEDIUM | Warning + ticket | - | 30 jours |
| LOW | Warning | - | 90 jours |
| SAST (Semgrep `--error`) | Blocage | `# nosemgrep` justifié en revue | - |

## Justification
- Données d'étudiants (notes, emails): confidentialité et intégrité critiques -> seuil strict (HIGH+).
- CRITICAL sans exception: exploitable à distance, impact maximal.
- Les scores CVSS sont des ordres de grandeur: ils ne mesurent pas l'exploitabilité dans notre contexte.
## Limites
Un pipeline vert ne prouve pas l'absence de failles (logique métier, IDOR non détectés par SAST).
