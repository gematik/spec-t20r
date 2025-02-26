#!/bin/bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml -n ingress-nginx # Erstellt Namespace ingress-nginx