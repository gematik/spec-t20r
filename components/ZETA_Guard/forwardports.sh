#!/bin/bash

# Forward ports for ZETA Guard
kubectl port-forward svc/prometheus-svc 9090:9090 -n vsdm2 &
kubectl port-forward svc/jaeger-svc 16686:16686 -n vsdm2 &
kubectl port-forward svc/grafana-svc -n vsdm2 3000:3000 &