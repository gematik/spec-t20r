#!/bin/bash

set -e  # Beendet das Skript bei einem Fehler

# Standardwerte
CLUSTER_NAME="zeta-guard"
INGRESS_PORT=80  # Standardport für Ingress
WORKER_COUNT=4   # Standardanzahl Worker Nodes
ISTIO=false # Standardmäßig Istio deaktiviert
DOCKERFILE_PATH="resource-server/src/Dockerfile" # Docker-Image, das in den Cluster geladen werden soll
DOCKER_IMAGE="rs-vsdm2-app:latest" # Docker-Image-Name

# Hilfe-Funktion
usage() {
    echo "Usage: $0 [-c|--cluster <name>] [-w|--workers <count>] [-i|--istio] [-h|--help]"
    echo ""
    echo "Optionen:"
    echo "  -c, --cluster <name>  Setzt den Namen des Kind-Clusters (Standard: zeta-guard)"
    echo "  -w, --workers <count> Setzt die Anzahl der Worker Nodes (Standard: 4)"
    echo "  -i, --istio           Installiert 'istio' im Cluster (Standard: deaktiviert)"
    echo "  -h, --help            Zeigt diese Hilfe an"
    echo ""
    echo "Requirements:"
    echo "  - docker   (https://docs.docker.com/get-docker/)"
    echo "  - kind     (https://kind.sigs.k8s.io/docs/user/quick-start/#installation)"
    echo "  - kubectl  (https://kubernetes.io/docs/tasks/tools/)"
    echo "  - istioctl (https://istio.io/latest/docs/setup/getting-started/)"
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
        -w|--workers)
            WORKER_COUNT="$2"
            shift 2
            ;;
        -i|--istio)
            ISTIO=true
            shift 1
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
echo "⚙️ Anzahl Worker Nodes: ${WORKER_COUNT}"
if $ISTIO; then
    echo "ℹ️ istio wird in ${CLUSTER_NAME} installiert."
else
    echo "ℹ️ istio wird nicht in ${CLUSTER_NAME} installiert. Verwende Option '-i' oder '--istio' um istio zu installieren."
fi

# Generiere die kind-config.yaml mit dynamischem Port und Worker Anzahl
CONFIG_FILE="./kind-config-${CLUSTER_NAME}.yaml"

cat <<EOF > "${CONFIG_FILE}"
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
EOF

# Füge Worker Nodes dynamisch hinzu
for ((i=1; i<=${WORKER_COUNT}; i++)); do
  cat <<EOF >> "${CONFIG_FILE}"
- role: worker
EOF
done

cat <<EOF >> "${CONFIG_FILE}"
- role: worker
  extraPortMappings:
  - containerPort: 80
    hostPort: ${INGRESS_PORT}   # Ingress-Port
EOF

echo "🚀 Verwende Cluster-Name: ${CLUSTER_NAME}"

#CONFIG_FILE="kind-zeta-guard/kind-config.yaml"
NAMESPACE_FILE="namespace/namespace.yaml"
INGRESS_FILE="ingress/ingress.yaml"
INGRESS_VSDM2_FILE="ingress/ingress-vsdm2.yaml"
ENVOY_FILE="envoy/envoy.yaml"
OPA_FILE="opa/opa.yaml"
ORY_FILE="ory/ory.yaml"
GEMATIK_SIEM_SECRET_FILE="otel-collector/gematik-siem-secret.yaml"
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
INGRESS_TRACING_FILE="ingress/ingress-tracing.yaml"

# Prüfen, ob Docker installiert ist
if ! command -v docker &>/dev/null; then
    echo "❌ 'docker' ist nicht installiert. Installiere es mit:"
    echo "👉 https://docs.docker.com/get-docker/"
    echo "ℹ️ Stelle sicher, dass Docker Desktop ausgeführt wird."
    echo "ℹ️ Falls permission denied Fehler auftreten, führe folgende Bafehle aus."
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

# Prüfen, ob kubectl installiert ist
if ! command -v kubectl &>/dev/null; then
    echo "❌ 'kubectl' ist nicht installiert. Installiere es mit:"
    echo "👉 https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Prüfen, ob istioctl installiert ist, falls Option gesetzt
if $ISTIO; then
    if ! command -v istioctl &>/dev/null; then
        echo "❌ 'istioctl' ist nicht installiert. Installiere es mit:"
        echo "👉 https://istio.io/latest/docs/setup/getting-started/"
        exit 1
    fi
fi

# Prüfen, ob der Kind-Cluster existiert
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster ${CLUSTER_NAME} existiert bereits. Lösche den Cluster..."
    kind delete cluster --name "${CLUSTER_NAME}"
fi

# Cluster neu erstellen
echo "Erstelle den Cluster ${CLUSTER_NAME} mit der Konfigurationsdatei ${CONFIG_FILE}..."
kind create cluster --name "${CLUSTER_NAME}" --config "${CONFIG_FILE}"

# ${CONFIG_FILE} löschen
rm "${CONFIG_FILE}"

# Warten, bis der Cluster verfügbar ist
echo "Warten, bis der Cluster verfügbar ist..."
echo ""
sleep 5  # Kleine Verzögerung, um sicherzustellen, dass der Cluster bereit ist

# Erstellen des Docker-Images für den Resource Server
echo "📦 Erstelle das Docker-Image ${DOCKER_IMAGE} aus ${DOCKERFILE_PATH}..."
docker build --no-cache -t "${DOCKER_IMAGE}" -f "${DOCKERFILE_PATH}" resource-server/src

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
# Warte bis das Ingress Controller Deployment bereit ist
echo "⏳ Warten auf das Ingress Controller Deployment..."
# sleep 30  # Kleine Verzögerung, um sicherzustellen, dass das Ingress Controller Deployment bereit ist
#kubectl wait --namespace projectcontour \
#  --for=condition=available --timeout=120s deployment/projectcontour
kubectl apply -f "${INGRESS_VSDM2_FILE}" # Erzeugt den Ingress für die VSDM2 App
kubectl apply -f "${ENVOY_FILE}" # Erzeugt den PEP HTTP Proxy
kubectl apply -f "${OPA_FILE}" # Erzeugt den OPA Service (Policy Engine)
kubectl apply -f "${ORY_FILE}" # Erzeugt die ORY Services (Authentifizierung und Autorisierung)
kubectl apply -f "${GEMATIK_SIEM_SECRET_FILE}" # Erzeugt das Geamtik SIEM Secret
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
# Ingress für Tracing aktivieren
kubectl apply -f "${INGRESS_TRACING_FILE}"

# Warten, bis die Ressourcen bereit sind
#echo "Warten, bis die Deployments hochgefahren sind..."
#kubectl wait --for=condition=available --timeout=600s deployment --all -n vsdm2

# Cluster-Überprüfung
echo "🔍 Prüfen, ob der Cluster korrekt funktioniert..."

echo "📌 Verfügbare Namespaces:"
kubectl get namespaces

echo "📌 Running Services:"
kubectl get svc -n vsdm2

echo "📌 Running Pods:"
kubectl get pods -A
#kubectl top pod -A
#echo "Status des horizontal pod autoscalers:"
#kubectl get hpa -A

#echo "📌 Ingress-Konfiguration:"
#kubectl get ingress -n vsdm2

# Rollout restart für alle Deployments
echo "🔄 Rollout restart für alle Deployments -im namespace projectcontour..."
kubectl rollout restart deployment -n projectcontour

# Istio Installation
if $ISTIO; then
    echo "🚀 Installiere istio in ${CLUSTER_NAME}..."
    istioctl install --set profile=ambient --skip-confirmation
    #kubectl label namespace default istio-injection=enabled
    #kubectl apply -f samples/addons
    kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
    kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml

fi
echo "✅ Skript erfolgreich abgeschlossen."
echo "Der Cluster ${CLUSTER_NAME} wurde erstellt."
echo ""
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