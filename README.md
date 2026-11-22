# EduGrade - Projet DevSecOps (ING-5-SSIR)
Application Flask + PostgreSQL (rôles student/teacher/admin), sécurisée du code à la production.
Voir docs/ et .gitlab-ci.yml. Tous les secrets sont des secrets de TEST. Tests offensifs uniquement sur cette application en local.
## Lancer en local
cp .env.example .env && pip install werkzeug && python3 db/gen_init.py && docker compose up --build
## Kubernetes
./scripts/k8s-setup.sh
