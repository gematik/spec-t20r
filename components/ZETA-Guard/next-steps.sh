#!/bin/bash

echo "Wie geht es weiter?"
# Port-Forwarding für Prometheus, Jaeger und Grafana
echo "🌐 Port-Forwarding für Prometheus, Grafana und Jaeger erst starten, wenn alle pods laufen."
echo "⏳ Warte bis alles läuft:"
echo "kubectl get pods -A | grep -v kube-system"
echo "📌 Dann Port-Forwarding:"
echo "./forwardports.sh"

# Teste den Zugriff auf die Services
echo "📌 Wenn alle pods laufen, kann man den Resource Server aufrufen:"
echo "curl -v http://localhost/vsdservice/v1/vsdmbundle"
echo "📌 Oder Last anlegen:"
echo "python ../ZETA-Client/vsdm2-loadgen/vsdm2-loadgen.py --rps=60 --duration=1000 --threads=2"
