# Monitoring with Prometheus and Grafana in Kubernetes

These are Kubernetes manifest files for deploying Prometheus and Grafana.  For simplicity, these manifests will set up basic Prometheus and Grafana instances. For production deployments, you'd likely need to configure persistence, security, resource requests/limits, and more advanced Prometheus configurations.

**1. Prometheus Manifests:**

*   **`prometheus-configmap.yaml` (ConfigMap for Prometheus Configuration):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yaml: |
    global:
      scrape_interval:     15s
      evaluation_interval: 15s

    # Alertmanager configuration
    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          # - alertmanager:9093

    # Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
    rule_files:
      # - "first_rules.yml"
      # - "second_rules.yml"

    # A scrape configuration containing exactly one endpoint to scrape:
    # Here it's Prometheus itself.
    scrape_configs:
      # By default, monitor prometheus itself.
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']

      # Example job to receive remote write data.
      - job_name: 'otel-remote-write'
        remote_write:
          - url: http://localhost:9090/api/v1/write # Prometheus's own write endpoint
            write_relabel_configs:
              - source_labels: [__name__]
                target_label: job
                regex: '(.*)'
                replacement: 'otel-traces' # Label for traces ingested via remote write

```

*   **`prometheus-deployment.yaml` (Deployment for Prometheus):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest # Use the official Prometheus image
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: prometheus-config-volume
              mountPath: /etc/prometheus/prometheus.yaml
              subPath: prometheus.yaml
      volumes:
        - name: prometheus-config-volume
          configMap:
            name: prometheus-config
```

*   **`prometheus-service.yaml` (Service for Prometheus):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
spec:
  selector:
    app: prometheus
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
  type: ClusterIP # Or LoadBalancer/NodePort if you need external access to Prometheus UI
```

**2. Grafana Manifests:**

*   **`grafana-deployment.yaml` (Deployment for Grafana):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:latest # Use the official Grafana image
          ports:
            - containerPort: 3000
```

*   **`grafana-service.yaml` (Service for Grafana):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grafana-service
spec:
  selector:
    app: grafana
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
  type: LoadBalancer # Or NodePort for external access
```

**Explanation:**

**Prometheus:**

*   **`prometheus-configmap.yaml`**:
    *   `global` section sets basic global scrape and evaluation intervals.
    *   `scrape_configs`:
        *   `job_name: 'prometheus'`:  Scrapes Prometheus itself on `localhost:9090`.
        *   `job_name: 'otel-remote-write'`:  This is important for receiving data from the OpenTelemetry Collector's `prometheusremotewrite` exporter.
            *   `remote_write`: Defines the remote write configuration.
                *   `url: http://localhost:9090/api/v1/write`: Points to Prometheus's own remote write endpoint.  **This configuration is for Prometheus to receive its *own* remote write data. In a real setup, you would point the OTel Collector's `prometheusremotewrite` exporter to `http://prometheus-service:9090/api/v1/write` (using the service name).** We are keeping it simple here for a basic example.
                *   `write_relabel_configs`: Adds a `job` label with the value `otel-traces` to all metrics received via remote write. This helps identify data coming from traces.
*   **`prometheus-deployment.yaml`**:
    *   Uses the official `prom/prometheus:latest` Docker image.
    *   Mounts the `prometheus-configmap.yaml` ConfigMap to configure Prometheus.
*   **`prometheus-service.yaml`**:
    *   Creates a `ClusterIP` service by default, making Prometheus accessible within the Kubernetes cluster (e.g., for the OpenTelemetry Collector to send data). You can change `type` to `LoadBalancer` or `NodePort` if you need to access the Prometheus UI externally.

**Grafana:**

*   **`grafana-deployment.yaml`**:
    *   Uses the official `grafana/grafana:latest` Docker image.
*   **`grafana-service.yaml`**:
    *   Creates a `LoadBalancer` service, making Grafana accessible externally via a cloud provider's load balancer (or you can use `NodePort` if LoadBalancer is not available in your environment).

**How to Deploy:**

1.  **Apply the Manifests:**
    ```bash
    kubectl apply -f prometheus-configmap.yaml
    kubectl apply -f prometheus-deployment.yaml
    kubectl apply -f prometheus-service.yaml
    kubectl apply -f grafana-deployment.yaml
    kubectl apply -f grafana-service.yaml
    ```

2.  **Access Grafana:**
    *   If you used `type: LoadBalancer` for `grafana-service`, get the external IP address of the service:
        ```bash
        kubectl get service grafana-service
        ```
        Look for the `EXTERNAL-IP`. Access Grafana in your browser using `http://<EXTERNAL-IP>:3000`.
    *   If you used `type: NodePort` for `grafana-service`, get the NodePort:
        ```bash
        kubectl get service grafana-service
        ```
        Look for the `PORT(S)` column, e.g., `3000:3XXXX/TCP`. Access Grafana in your browser using `http://<Kubernetes-Node-IP>:<3XXXX>`.

3.  **Configure Grafana Data Source:**
    *   Log in to Grafana (default username/password is `admin/admin`). You'll likely be prompted to change the password.
    *   Go to "Configuration" -> "Data sources".
    *   Click "Add data source".
    *   Choose "Prometheus".
    *   For the "HTTP URL", enter `http://prometheus-service:9090`.  This uses the Kubernetes service name to connect to Prometheus within the cluster.
    *   Click "Save & test". You should see a "Data source is working" message.

4.  **Explore Metrics:**
    *   Go to "Create" -> "Dashboard".
    *   Add a new panel.
    *   Choose "Prometheus" as the data source.
    *   Start writing PromQL queries in the "Query" field to explore metrics. For example, try querying for `up` (a standard Prometheus metric indicating service uptime) or the `otel-traces_.*` metrics that might be generated by the OTel Collector's `prometheusremotewrite` exporter (if you have configured it correctly and are sending trace data).

**Important Considerations:**

*   **Persistence:**  These manifests do *not* include persistent storage for Prometheus or Grafana.  In a real-world setup, you would definitely want to add Persistent Volume Claims (PVCs) to store Prometheus time-series data and Grafana dashboards/configurations.
*   **Resource Limits/Requests:** For production, add resource requests and limits to the container specifications in the Deployments to ensure resource management and stability.
*   **Security:** Basic authentication for Grafana is enabled by default. For production, configure proper authentication and authorization for both Prometheus and Grafana, especially if they are exposed externally. Consider using HTTPS/TLS.
*   **Prometheus Configuration:** The provided `prometheus.yaml` is very basic. You will need to customize it for your specific monitoring needs, including defining scrape targets for your applications and services, alert rules, and more advanced settings.
*   **Remote Write Configuration (OTel Collector)**:  Remember to update the `otel-collector-configmap-prometheus.yaml` to point the `prometheusremotewrite` exporter to the correct `prometheus-service:9090/api/v1/write` endpoint so that the OTel Collector sends data to your Prometheus instance.

This setup provides a basic Prometheus and Grafana stack in Kubernetes. You can build upon these manifests to create a more robust and production-ready monitoring solution.