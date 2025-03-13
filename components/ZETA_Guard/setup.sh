#!/bin/bash

set -e  # Beendet das Skript bei einem Fehler

# Standardwerte
CLUSTER_NAME="zeta-guard"
INGRESS_PORT=80  # Standardport für Ingress

# Hilfe-Funktion
usage() {
    echo "Usage: $0 [-c|--cluster <name>] [-p|--port <port>] [-h|--help]"
    echo ""
    echo "Optionen:"
    echo "  -c, --cluster <name>  Setzt den Namen des Kind-Clusters (Standard: zeta-guard)"
    echo "  -p, --port <port>     Setzt den Host-Port für Ingress (Standard: 80)"
    echo "  -h, --help            Zeigt diese Hilfe an"
    echo ""
    echo "Requirements:"
    echo "  - docker   (https://docs.docker.com/get-docker/)"
    echo "  - kind     (https://kind.sigs.k8s.io/docs/user/quick-start/#installation)"
    echo "  - kubectl  (https://kubernetes.io/docs/tasks/tools/)"
    echo ""
    echo "Hinweis: Die Installation mit snap (Ubuntu) führt zu Fehlern."
    echo "         Verwende apt install."   
    exit 0
}

# Kommandozeilen-Argumente verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--cluster)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -p|--port)
            INGRESS_PORT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "❌ Ungültige Option: $1"
            usage
            ;;
    esac
done

echo "🚀 Verwende Cluster-Name: ${CLUSTER_NAME}"
echo "🌐 Ingress wird auf Port ${INGRESS_PORT} gebunden"

# Generiere die kind-config.yaml mit dynamischem Port
CONFIG_FILE="./kind-config-${CLUSTER_NAME}.yaml"

cat <<EOF > "${CONFIG_FILE}"
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
- role: worker
- role: worker
- role: worker
- role: worker
  extraPortMappings:
  - containerPort: 80
    hostPort: ${INGRESS_PORT}   # Dynamischer Ingress-Port
EOF

echo "🚀 Verwende Cluster-Name: ${CLUSTER_NAME}"

#CONFIG_FILE="kind-zeta-guard/kind-config.yaml"
NAMESPACE_FILE="namespace/namespace.yaml"
INGRESS_FILE="ingress/ingress.yaml"
INGRESS_VSDM2_FILE="ingress/ingress-vsdm2.yaml"
ENVOY_FILE="envoy/envoy.yaml"
OPA_FILE="opa/opa.yaml"
ORY_FILE="ory/ory.yaml"
OTEL_COLLECTOR_FILE="otel-collector/otel-collector.yaml"
PROMETHEUS_FILE="prometheus/prometheus.yaml"
JAEGER_FILE="jaeger/jaeger.yaml"
GRAFANA_FILE="grafana/grafana.yaml"
RESOURCE_SERVER_FILE="resource-server/rs-vsdm2-app.yaml"
VALKEY_PDP_FILE="valkey-pdp/valkey-pdp.yaml"
VALKEY_PEP_FILE="valkey-pep/valkey-pep.yaml"
BDE_COLLECTOR_FILE="bde-collector/bde-collector.yaml"
METRICS_SERVER_FILE="metrics-server/metrics-server.yaml"
HPA_FILE="metrics-server/horizontal-pod-autoscaler.yaml"

# Docker-Image, das in den Cluster geladen werden soll
DOCKERFILE_PATH="resource-server/src/Dockerfile"
DOCKER_IMAGE="rs-vsdm2-app:latest"

# Prüfen, ob Docker installiert ist
if ! command -v docker &>/dev/null; then
    echo "❌ 'docker' ist nicht installiert. Installiere es mit:"
    echo "👉 https://docs.docker.com/get-docker/"
    echo "ℹ️ Stelle sicher, dass Docker Desktop ausgeführt wird."
    echo "ℹ️ Falls permission denied Fehler auftreten, führe folgende Befehle aus."
    echo "ℹ️ sudo groupadd docker"
    echo "ℹ️ sudo usermod -aG docker $USER"
    echo "ℹ️ newgrp docker"
    echo "ℹ️ docker run hello-world"
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
docker build -t "${DOCKER_IMAGE}" -f "${DOCKERFILE_PATH}" resource-server/src

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

# Konfiguriere kubectl für den Zugriff auf den Cluster
echo "Konfiguriere kubectl für den Zugriff auf den Cluster..."
kubectl config use-context kind-${CLUSTER_NAME}

# Manifest Dateien anwenden
echo "Wende die Manifest Dateien an..."
kubectl label node "${CLUSTER_NAME}"-worker ingress-ready=true # Label hinzufügen, um Ingress auf einem Worker-Node aktivieren zu können
kubectl apply -f "${NAMESPACE_FILE}" # Erzeugt den Namespace vsdm2
kubectl apply -f "${INGRESS_FILE}" # Erzeugt den Ingress Controller
# Warte bis der Ingress Controller Deployment bereit ist
#echo "⏳ Warten auf Ingress Controller Deployment..."
#kubectl wait --namespace projectcontour \
#  --for=condition=available --timeout=120s deployment/projectcontour
kubectl apply -f "${INGRESS_VSDM2_FILE}" # Erzeugt den Ingress für die VSDM2 App
kubectl apply -f "${ENVOY_FILE}" # Erzeugt den PEP HTTP Proxy
kubectl apply -f "${OPA_FILE}" # Erzeugt den OPA Service (Policy Engine)
kubectl apply -f "${ORY_FILE}" # Erzeugt die ORY Services (Authentifizierung und Autorisierung)
kubectl apply -f "${OTEL_COLLECTOR_FILE}" # Erzeugt den OpenTelemetry Collector (Telemetrie-Daten Service)
kubectl apply -f "${PROMETHEUS_FILE}" # Erzeugt den Prometheus Service (Monitoring)
kubectl apply -f "${JAEGER_FILE}" # Erzeugt den Jaeger Service (Tracing)
kubectl apply -f "${GRAFANA_FILE}" # Erzeugt den Grafana Service (Dashboard)
kubectl apply -f "${RESOURCE_SERVER_FILE}" # Erzeugt den Resource Server Service (VSDM2 App)
kubectl apply -f "${VALKEY_PDP_FILE}" # Erzeugt die PDP DB Service (ValKey)
kubectl apply -f "${VALKEY_PEP_FILE}" # Erzeugt den PEP DB Service (ValKey)
kubectl apply -f "${BDE_COLLECTOR_FILE}" # Erzeugt den BDE Collector Service (otel-collector für BDE)
kubectl apply -f "${METRICS_SERVER_FILE}" # Erzeugt den Metrics Server (Ressourcenverbrauch)
kubectl apply -f "${HPA_FILE}" # Erzeugt den Horizontal Pod Autoscaler (HPA)

# Warten, bis die Ressourcen bereit sind
echo "Warten, bis die Deployments hochgefahren sind..."
kubectl wait --for=condition=available --timeout=120s deployment --all -n vsdm2

# Cluster-Überprüfung
echo "🔍 Prüfen, ob der Cluster korrekt funktioniert..."

echo "📌 Verfügbare Namespaces:"
kubectl get namespaces

echo "📌 Running Pods:"
kubectl get pods -A
kubectl top pod -A
kubectl get hpa -A

echo "📌 Running Services:"
kubectl get svc -n vsdm2

echo "📌 Ingress-Konfiguration:"
kubectl get ingress -n vsdm2

# Port-Forwarding für Prometheus, Jaeger und Grafana
echo "🚀 Port-Forwarding für Prometheus..."
kubectl port-forward svc/prometheus-svc 9090:9090 -n vsdm2 &
echo "Prometheus ist unter http://localhost:9090 erreichbar."
echo "Beispielabfrage: http://localhost:9090/graph?g0.range_input=1h&g0.expr=up&g0.tab=0"
echo "Port-Forwarding für Jaeger..."
kubectl port-forward svc/jaeger-svc 16686:16686 -n vsdm2 &
echo "Jaeger ist unter http://localhost:16686 erreichbar."
echo "Port-Forwarding für Grafana..."
kubectl port-forward svc/grafana-svc 3000:3000 -n vsdm2 &
echo "Grafana ist unter http://localhost:3000 erreichbar."

echo "Status des horizontal pod autoscaler:"
kubectl get hpa -A

# Teste den Zugriff auf die Services
echo "Resource Server Service:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/vsdservice/v1/vsdmbundle

echo "✅ Skript erfolgreich abgeschlossen."
echo "Der Cluster ${CLUSTER_NAME} wurde erstellt und ist einsatzbereit."
echo "Du kannst den Cluster mit 'kind delete cluster --name ${CLUSTER_NAME}' löschen."
