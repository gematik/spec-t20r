#!/bin/bash

set -e  # Beendet das Skript bei einem Fehler

CLUSTER_NAME="zeta-guard"
CONFIG_FILE="kind-zeta-guard/kind-config.yaml"
INGRESS_FILE="ingress/ingress.yaml"
ENVOY_FILE="envoy/envoy.yaml"
HELLO_FILE="hello-world/hello-world.yaml"
OPA_FILE="opa/opa.yaml"
ORY_FILE="ory/ory.yaml"
OTEL_COLLECTOR_FILE="otel-collector/otel-collector.yaml"
PROMETHEUS_FILE="prometheus/prometheus.yaml"
JAEGER_FILE="jaeger/jaeger.yaml"
RESOURCE_SERVER_FILE="resource_server/rs-vsdm2-app.yaml"
VALKEY_PDP_FILE="valkey-pdp/valkey-pdp.yaml"
VALKEY_PEP_FILE="valkey-pep/valkey-pep.yaml"

# Docker-Image, das in den Cluster geladen werden soll
DOCKERFILE_PATH="resource_server/src/Dockerfile"
DOCKER_IMAGE="rs-vsdm2-app:latest"

# Prüfen, ob Docker installiert ist
if ! command -v docker &>/dev/null; then
    echo "❌ 'docker' ist nicht installiert. Installiere es mit:"
    echo "👉 https://docs.docker.com/get-docker/"
    exit 1
fi

# Prüfen, ob kind installiert ist
if ! command -v kind &>/dev/null; then
    echo "❌ 'kind' ist nicht installiert. Installiere es mit:"
    echo "👉 https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Erstellen des Docker-Images für den Resource Server
echo "📦 Erstelle das Docker-Image ${DOCKER_IMAGE} aus ${DOCKERFILE_PATH}..."
docker build -t "${DOCKER_IMAGE}" -f "${DOCKERFILE_PATH}" resource_server/src

# Prüfen, ob der Kind-Cluster existiert
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster ${CLUSTER_NAME} existiert bereits. Lösche den Cluster..."
    kind delete cluster --name "${CLUSTER_NAME}"
fi

# Cluster neu erstellen
echo "Erstelle den Cluster ${CLUSTER_NAME} mit der Konfigurationsdatei ${CONFIG_FILE}..."
kind create cluster --name "${CLUSTER_NAME}" --config "${CONFIG_FILE}"


# Warten, bis der Cluster verfügbar ist
echo "Warten, bis der Cluster verfügbar ist..."
echo ""
sleep 5  # Kleine Verzögerung, um sicherzustellen, dass der Cluster bereit ist

# Docker-Image in Kind-Cluster laden
echo "Lade das Docker-Image ${DOCKER_IMAGE} in den Kind-Cluster..."
kind load docker-image "${DOCKER_IMAGE}" --name "${CLUSTER_NAME}"

# Manifest Dateien anwenden
echo "Wende die Manifest Dateien an..."
kubectl label node zeta-guard-worker ingress-ready=true # Label hinzufügen, um Ingress auf einem Worker-Node aktivieren zu können
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml -n ingress-nginx # Erzeugt Namespace ingress-nginx
kubectl apply -f "${INGRESS_FILE}" # Erzeugt namespace vsdm2
kubectl apply -f "${ENVOY_FILE}" # Erzeugt den PEP HTTP Proxy
kubectl apply -f "${HELLO_FILE}" # Erzeugt den Hello-World Service, der von der Ingress-Ressource erreichbar ist
kubectl apply -f "${OPA_FILE}" # Erzeugt den OPA Service (Policy Engine)
kubectl apply -f "${ORY_FILE}" # Erzeugt die ORY Services (Authentifizierung und Autorisierung)
kubectl apply -f "${OTEL_COLLECTOR_FILE}" # Erzeugt den OpenTelemetry Collector (Telemetrie-Daten Service)
kubectl apply -f "${PROMETHEUS_FILE}" # Erzeugt den Prometheus Service (Monitoring)
kubectl apply -f "${JAEGER_FILE}" # Erzeugt den Jaeger Service (Tracing)
kubectl apply -f "${RESOURCE_SERVER_FILE}" # Erzeugt den Resource Server Service (VSDM2 App)
kubectl apply -f "${VALKEY_PDP_FILE}" # Erzeugt die PDP DB Service (ValKey)
kubectl apply -f "${VALKEY_PEP_FILE}" # Erzeugt den PEP DB Service (ValKey)

# Warten, bis die Ressourcen bereit sind
echo "Warten, bis die Deployments hochgefahren sind..."
kubectl wait --for=condition=available --timeout=120s deployment --all -n vsdm2

# Cluster-Überprüfung
echo "🔍 Prüfen, ob der Cluster korrekt funktioniert..."

echo "📌 Verfügbare Namespaces:"
kubectl get namespaces

echo "📌 Running Pods:"
kubectl get pods -n vsdm2

echo "📌 Running Services:"
kubectl get svc -n vsdm2

echo "📌 Ingress-Konfiguration:"
kubectl get ingress -n vsdm2

# Teste den Zugriff auf die Services
echo "📌 Teste den Zugriff auf die Ingress-Routen..."
echo "Hello-World Service:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/hello

echo "Prometheus Service:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/query

echo "Resource Server Service:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/vsdservice/v1/vsdmbundle

echo "✅ Skript erfolgreich abgeschlossen."
echo "Der Cluster ${CLUSTER_NAME} wurde erstellt und ist einsatzbereit."
echo "Du kannst den Cluster mit 'kind delete cluster --name ${CLUSTER_NAME}' löschen."
echo "Die Ingress-Ressource wurde angewendet und ist einsatzbereit."
echo "Die Services wurden bereitgestellt und sind einsatzbereit."

# Port-Forwarding für Prometheus
echo "🚀 Port-Forwarding für Prometheus..."
kubectl port-forward svc/prometheus-svc 9090:9090 -n vsdm2 &
echo "Prometheus ist unter http://localhost:9090 erreichbar."
echo "Beispielabfrage: http://localhost:9090/graph?g0.range_input=1h&g0.expr=up&g0.tab=0"
echo "Port-Forwarding für Jaeger..."
kubectl port-forward svc/jaeger-query-svc 16686:16686 -n vsdm2 &
echo "Jaeger ist unter http://localhost:16686 erreichbar."
