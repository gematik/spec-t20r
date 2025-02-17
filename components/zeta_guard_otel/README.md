# ZETA Guard Telemetrie-Daten Service

To create an OpenTelemetry Collector and Exporter for Kubernetes that sends data to a Prometheus instance, we will use the `prometheusremotewrite` exporter.  As discussed earlier, Prometheus is primarily for metrics, so we'll be exporting trace data in a way that Prometheus can ingest as metrics.

Here are the Kubernetes manifest files:

**1. `otel-collector-configmap-prometheus.yaml` (ConfigMap for OpenTelemetry Collector Configuration):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config-prometheus
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317

    processors:
      batch:

    exporters:
      prometheusremotewrite:
        endpoint: http://prometheus-service:9090/api/v1/write # Replace with your Prometheus service endpoint
        # Optional: Authentication if your Prometheus instance requires it
        # auth:
        #   basicauth:
        #     username: "your_username"
        #     password: "your_password"
        # Optional: TLS settings if Prometheus uses HTTPS
        # tls:
        #   insecure_skip_verify: true # Only for testing, disable in production
        #   ca_file: "/path/to/ca.crt"

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheusremotewrite]
```

**2. `otel-collector-deployment-prometheus.yaml` (Deployment for OpenTelemetry Collector):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector-prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector-prometheus
  template:
    metadata:
      labels:
        app: otel-collector-prometheus
    spec:
      containers:
        - name: otel-collector-prometheus
          image: otel/opentelemetry-collector-contrib:latest
          ports:
            - containerPort: 4317 # OTLP gRPC
          volumeMounts:
            - name: otel-collector-config-volume
              mountPath: /etc/otel-collector-config.yaml
              subPath: otel-collector-config.yaml
      volumes:
        - name: otel-collector-config-volume
          configMap:
            name: otel-collector-config-prometheus # Use the Prometheus ConfigMap
```

**3. `otel-collector-service-prometheus.yaml` (Service for OpenTelemetry Collector):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: otel-collector-service-prometheus
spec:
  selector:
    app: otel-collector-prometheus
  ports:
    - protocol: TCP
      port: 4317
      targetPort: 4317
  type: ClusterIP # Internal service, accessed by Envoy and rs-vsdm2-server
```

**Explanation of Changes:**

*   **ConfigMap (`otel-collector-configmap-prometheus.yaml`)**:
    *   **`exporters.prometheusremotewrite`**:  This section is now configured to use the `prometheusremotewrite` exporter.
        *   **`endpoint`**:  **Important:** You need to replace `http://prometheus-service:9090/api/v1/write` with the actual endpoint of your Prometheus instance within your Kubernetes cluster.  `prometheus-service:9090` assumes you have a Prometheus Service named `prometheus-service` running in the same namespace (or accessible via DNS).  Adjust the service name and namespace if needed. The default Prometheus port is 9090, and the remote write endpoint is `/api/v1/write`.
        *   **`auth` and `tls` (Optional)**:  If your Prometheus instance requires authentication or uses HTTPS with TLS, uncomment and configure the `auth` and `tls` sections accordingly.  For basic authentication, provide `username` and `password`. For TLS, you might need to configure `ca_file` to point to a certificate authority file if Prometheus uses a self-signed certificate or a certificate from a private CA. **For testing, `tls.insecure_skip_verify: true` can be used, but it's highly discouraged in production as it bypasses TLS certificate verification.**

*   **Deployment and Service (`otel-collector-deployment-prometheus.yaml`, `otel-collector-service-prometheus.yaml`)**:
    *   The `metadata.name` and `spec.selector.matchLabels.app`, `spec.template.metadata.labels.app` have been updated to `-prometheus` to differentiate these resources from the previous collector setup (if you are running both).
    *   In `otel-collector-deployment-prometheus.yaml`, the `configMap.name` in the `volumes` section is updated to `otel-collector-config-prometheus` to use the new Prometheus-specific ConfigMap.

**How to Deploy and Use:**

1.  **Ensure Prometheus is Running in Kubernetes**:  Before deploying the collector, make sure you have a Prometheus instance already running and accessible within your Kubernetes cluster.  You might have deployed Prometheus using Helm, Operator, or manual manifests.
2.  **Adjust Prometheus Endpoint**:  **Crucially**, edit `otel-collector-configmap-prometheus.yaml` and replace `http://prometheus-service:9090/api/v1/write` with the correct endpoint for your Prometheus service.
3.  **Apply the Manifests**:
    ```bash
    kubectl apply -f otel-collector-configmap-prometheus.yaml
    kubectl apply -f otel-collector-deployment-prometheus.yaml
    kubectl apply -f otel-collector-service-prometheus.yaml
    ```
4.  **Update Envoy and `rs_vsdm2` Server**:
    *   If you want to use this Prometheus-exporter collector, you need to update the `envoy-configmap.yaml` and `rs-vsdm2-deployment.yaml` to point to the new service name: `otel-collector-service-prometheus`.
    *   **`envoy-configmap.yaml` (Update `otel_collector_cluster` in `clusters` and `tracing.http.grpc_service.envoy_grpc`)**:
        ```yaml
        # ... other envoy config ...
        clusters:
          # ... rs_vsdm2_cluster definition ...
          - name: otel_collector_cluster
            # ... other cluster settings ...
            load_assignment:
              cluster_name: otel_collector_cluster
              endpoints:
                - lb_endpoints:
                    - endpoint:
                        address:
                          socket_address:
                            address: otel-collector-service-prometheus # Updated service name
                            port_value: 4317
        # ... tracing section ...
        tracing:
          http:
            # ... other tracing config ...
            typed_config:
              # ...
              grpc_service:
                envoy_grpc:
                  cluster_name: otel_collector_cluster # Still use cluster name, but cluster points to new service
        ```
    *   **`rs-vsdm2-deployment.yaml` (Update `env.OTLP_ENDPOINT`)**:
        ```yaml
        # ... rs-vsdm2-deployment.yaml ...
        spec:
          # ...
          containers:
            - name: rs-vsdm2-server
              # ...
              env:
                - name: OTLP_ENDPOINT
                  value: otel-collector-service-prometheus:4317 # Updated service name
        ```
    *   Re-apply the updated Envoy and `rs_vsdm2` manifests after making these changes.

**Important Considerations and Limitations (Reiterated):**

*   **Trace Data as Metrics**:  Remember that Prometheus is optimized for time-series metrics. Exporting trace data as metrics using `prometheusremotewrite` is not the typical way to visualize or analyze traces in detail. You will likely not see individual spans or trace timelines in Prometheus.
*   **Metric Conversion**: The `prometheusremotewrite` exporter will attempt to convert trace data into Prometheus metrics. The effectiveness and interpretability of these metrics depend on how the exporter handles the conversion, and it might not be ideal for in-depth trace analysis.
*   **Alternative: `spanmetrics` Processor + Prometheus Exporter**: For getting *meaningful metrics derived from traces* into Prometheus, consider using the `spanmetrics` processor in the OpenTelemetry Collector. This processor can generate metrics like request duration, error rates, etc., from spans, which are more suitable for Prometheus. You would then use a standard Prometheus exporter (like the built-in Prometheus receiver in the collector or a separate Prometheus client) to expose these metrics for Prometheus to scrape.
*   **Dedicated Tracing Backends**: For comprehensive trace visualization, analysis, and querying, it is highly recommended to use a dedicated tracing backend like Jaeger, Zipkin, or Tempo and configure an appropriate OpenTelemetry exporter for one of those systems instead of directly exporting traces to Prometheus.

Use this configuration if you specifically need to send *some form* of trace-related data to Prometheus, understanding its limitations for detailed trace analysis. If you require proper trace visualization and analysis, consider using a dedicated tracing backend.