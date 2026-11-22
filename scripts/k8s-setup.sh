#!/usr/bin/env bash
set -euo pipefail
kind create cluster --name edugrade --config k8s/kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml
kubectl -n kube-system rollout status ds/calico-node --timeout=300s
kubectl create namespace edugrade
kubectl -n edugrade create secret generic edugrade-secrets \
  --from-literal=JWT_SECRET="$(openssl rand -hex 32)" \
  --from-literal=DB_PASSWORD="$(openssl rand -hex 16)"
kubectl -n edugrade create configmap init-sql --from-file=db/init.sql
docker build -t edugrade:1.0 app/
kind load docker-image edugrade:1.0 --name edugrade
helm repo add kyverno https://kyverno.github.io/kyverno/ && helm repo update
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
kubectl -n kyverno rollout status deploy --timeout=300s
kubectl apply -f k8s/kyverno.yaml
kubectl apply -f k8s/postgres.yaml -f k8s/app.yaml
kubectl -n edugrade rollout status deploy/postgres --timeout=180s
kubectl -n edugrade rollout status deploy/edugrade --timeout=180s
kubectl apply -f k8s/netpol.yaml
kubectl -n edugrade get pods
