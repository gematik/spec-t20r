#!/bin/bash

echo "🚀 Port-Forwarding für Prometheus..."
echo "Prometheus ist unter http://localhost:9090 erreichbar."
echo "Beispielabfrage: http://localhost:9090/graph?g0.range_input=1h&g0.expr=up&g0.tab=0"
echo "Port-Forwarding für Jaeger..."
echo "Jaeger ist unter http://localhost:16686 erreichbar."
echo "Port-Forwarding für Grafana..."
echo "Grafana ist unter http://localhost:3000 erreichbar."

# Forward ports for ZETA Guard
kubectl port-forward svc/prometheus-svc 9090:9090 -n vsdm2 &
kubectl port-forward svc/jaeger-svc 16686:16686 -n vsdm2 &
kubectl port-forward svc/grafana-svc -n vsdm2 3000:3000 &
