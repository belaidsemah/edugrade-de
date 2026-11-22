#!/usr/bin/env bash
# Rejoue l'enumeration IDOR (detection Grafana). Usage: TOKEN=... ./scripts/idor-replay.sh
for i in $(seq 1 10); do curl -s -o /dev/null -w "%{http_code} " -H "Authorization: Bearer $TOKEN" http://localhost:5000/grades/$i; done; echo
