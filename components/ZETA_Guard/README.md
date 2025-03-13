# ZETA Guard

ZETA Guard ist eine Implementierung eines Zero Trust PEP und PDP für Resource Server der TI 2.0. 

## Installation

ZETA Guard ist ein Kubernetes kind Service und kann mit dem folgenden Befehl installiert werden:

```bash
./setup.sh --cluster <cluster-name>
```

## Komponenten

ZETA Guard besteht aus folgenden Komponenten:

- ZETA Guard PEP: 
  - HTTP Proxy: envoy-pep-svc
  - PEP DB: valkey-pep-svc
- ZETA Guard PDP: 
  - Authorization Server: ory-hydra-svc und valkey-as-svc
  - Policy Engine: opa-svc
- Telemetrie-Daten Service: otel-collector-svc
- Monitoring:
  - Prometheus: prometheus-svc
  - Jaeger: jaeger-collector-svc, jaeger-query-svc