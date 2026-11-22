# Plan de réponse à incident: énumération IDOR sur /grades
| Phase | Action | Outil |
|---|---|---|
| Détecter | Alerte: > 5 access_denied / minute | Grafana + Loki |
| Contenir | Désactiver le compte, révoquer JWT_SECRET, bloquer l'IP | kubectl |
| Éradiquer | Patch + MR + pipeline vert | GitLab CI |
| Rétablir | kubectl rollout vers image saine | kubectl |
| Apprendre | Post-mortem, nouvelle règle d'alerte | doc |

## Timeline de la démo
T0 attaque rejouée: __:__ | T+ détection: __:__ | T+ confinement: __:__ | T+ rétablissement: __:__
