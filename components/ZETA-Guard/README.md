# ZETA Guard

ZETA Guard ist eine Implementierung eines Zero Trust PEP und PDP für Resource Server der TI 2.0. 

## Installation

ZETA Guard ist ein Kubernetes kind Service und kann mit dem folgenden Befehl installiert werden:

```bash
./setup.sh
```

### Fehlerbehebung

Falls die Installation fehlschlägt, kann das daran liegen, dass zu wenig Ressourcen verfügbar sind.

- Fehler: Joining worker nodes failed
  
  Behebung: Editiere die Datei `/etc/sysctl.conf` und füge folgende Zeilen hinzu:
  ```bash
  fs.inotify.max_user_watches = 524288
  fs.inotify.max_user_instances = 512
  ```


## Komponenten

![OpenTelemetry PoC](/images/opentelemetry-poc.svg)

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