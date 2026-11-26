#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

pause() {
  echo -e "\n${CYAN}>>> Appuie sur [ENTRÉE] pour passer à l'étape suivante...${NC}"
  read -r
}

clear
echo -e "${CYAN}=====================================================${NC}"
echo -e "${CYAN}   DÉMONSTRATION DEVSECOPS — PLATEFORME EDUGRADE     ${NC}"
echo -e "${CYAN}=====================================================${NC}"

echo -e "\n${GREEN}[ÉTAPE 1] Vérification des Secrets (Gitleaks)${NC}"
gitleaks detect --source . -v
pause

echo -e "\n${GREEN}[ÉTAPE 2] Audit de Sécurité de l'Image Docker (Trivy)${NC}"
trivy image --severity HIGH,CRITICAL --ignore-unfixed edugrade:secure
pause

echo -e "\n${GREEN}[ÉTAPE 3] Architecture Kubernetes Durcie & Kyverno (Admission Control)${NC}"
kubectl get pods,svc,netpol,secret,sa -n edugrade
echo -e "\n${RED}>>> Test d'intrusion : tentative de déploiement d'un conteneur ROOT (UID 0)...${NC}"
kubectl run evil-root-pod -n edugrade --image=nginx --overrides='{"spec":{"securityContext":{"runAsNonRoot":false,"runAsUser":0}}}' || true
pause

echo -e "\n${GREEN}[ÉTAPE 4] Tests de l'API Durcie en Runtime (JWT, Anti-IDOR & Anti-SQLi)${NC}"
pkill -f "port-forward" 2>/dev/null || true
kubectl port-forward -n edugrade svc/edugrade-svc 8081:80 --address 0.0.0.0 >/dev/null 2>&1 &
sleep 2

echo -e "\n1) Connexion légitime (alice) :"
TOKEN=$(curl -s -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"AliceStrong#2026"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token JWT reçu : ${TOKEN:0:35}..."

echo -e "\n2) Accès légitime aux notes d'Alice (/api/grades/1) -> 200 OK :"
curl -i -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/grades/1

echo -e "\n\n3) Tentative d'attaque IDOR sur les notes de Bob (/api/grades/2) -> 403 Forbidden :"
curl -i -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/grades/2

echo -e "\n\n4) Tentative d'Injection SQL sur /login -> 400 Invalid input :"
curl -i -s -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'\'' OR '\''1'\''='\''1'\'' --","password":"123"}'

echo -e "\n\n${CYAN}=====================================================${NC}"
echo -e "${CYAN}   FIN DE LA DÉMONSTRATION — TOUS CONTRÔLES VALIDÉS  ${NC}"
echo -e "${CYAN}=====================================================${NC}"
