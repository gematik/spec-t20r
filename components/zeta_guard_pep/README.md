# Envoy Proxy (PEP)

## envoy.yaml

```yaml
# envoy.yaml
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      protocol: TCP
      address: 0.0.0.0
      port_value: 9901

static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          protocol: TCP
          address: 0.0.0.0
          port_value: 8081 # Envoy proxy listening port
      filter_chains:
        - filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
              stat_prefix: ingress_http
              access_log:
                - name: envoy.access_loggers.stdout
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.access_loggers.stream.v3.StdoutAccessLog
                    format: "[%START_TIME%] \"%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%\" %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% %RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)% [%UPSTREAM_CLUSTER%] [%UPSTREAM_HOST%] [%REQ(X-REQUEST-ID)%] trace_id=%TRACE_ID% span_id=%SPAN_ID% parent_span_id=%PARENT_SPAN_ID%\n"
              http_filters:
                - name: envoy.filters.http.opentelemetry_http
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.http.opentelemetry.v3.OpenTelemetryConfig
                    service_name: envoy-proxy-vsdm2
                    emit_attributes_as_spans: true
                    status_on_error:
                      code: 500
                    grpc_service:
                      envoy_grpc:
                        cluster_name: otel_collector_cluster
                        initial_metadata: []
                - name: envoy.filters.http.router
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
              route_config:
                name: local_route
                virtual_hosts:
                  - name: local_service
                    domains: ["*"]
                    routes:
                      - match:
                          prefix: "/" # Route all requests
                        route:
                          cluster: rs_vsdm2_cluster
                          timeout: 10s # Example timeout

  clusters:
    - name: rs_vsdm2_cluster
      connect_timeout: 0.25s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: rs_vsdm2_cluster
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: rs-vsdm2-service # Kubernetes service name of rs_vsdm2 server
                      port_value: 8080 # Port of rs_vsdm2 server

    - name: otel_collector_cluster
      connect_timeout: 0.25s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      http2_protocol_options: {} # Required for gRPC
      load_assignment:
        cluster_name: otel_collector_cluster
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: otel-collector-service # Kubernetes service name of otel-collector
                      port_value: 4317 # OTLP gRPC port

tracing:
  http:
    name: envoy.tracers.opentelemetry
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.OpenTelemetryConfig
      service_name: envoy-proxy-vsdm2-global # Global tracer service name
      grpc_service:
        envoy_grpc:
          cluster_name: otel_collector_cluster
          initial_metadata: []
      context_export_sampled: true # Export even sampled traces
      context_export_unsampled: false # Don't export unsampled traces (adjust as needed)
      resource_attributes:
        - key: deployment.environment
          value:
            string_value: "kubernetes" # Example environment attribute
```

**Explanation:**

*   **`admin`**: Defines the Envoy admin interface on port 9901 (for health checks, stats, etc.).
*   **`static_resources.listeners`**:
    *   Defines a listener named `listener_0` on port 8081, which is the port where Envoy will listen for incoming requests.
    *   **`filter_chains.filters.name: envoy.filters.network.http_connection_manager`**: Configures the HTTP Connection Manager, which handles HTTP requests.
        *   **`stat_prefix: ingress_http`**:  Prefix for statistics related to this connection manager.
        *   **`access_log`**: Configures access logging to stdout with a custom format that includes trace information (`trace_id`, `span_id`, `parent_span_id`).
        *   **`http_filters`**: Defines HTTP filters to be applied to requests.
            *   **`envoy.filters.http.opentelemetry_http`**:  **OpenTelemetry HTTP Filter**:
                *   `service_name: envoy-proxy-vsdm2`: Sets the service name for traces generated by this filter.
                *   `emit_attributes_as_spans: true`: Configures attributes to be emitted as spans.
                *   `status_on_error`: Sets HTTP status code 500 on error.
                *   `grpc_service.envoy_grpc.cluster_name: otel_collector_cluster`: Specifies the `otel_collector_cluster` cluster to send traces to via gRPC.
            *   **`envoy.filters.http.router`**: **Router Filter**: Routes requests based on configured routes.
        *   **`route_config.virtual_hosts.routes`**: Defines routing rules.
            *   `match.prefix: "/"`: Matches all requests (prefix matching `/`).
            *   `route.cluster: rs_vsdm2_cluster`: Routes matched requests to the `rs_vsdm2_cluster` cluster.
            *   `route.timeout: 10s`: Sets a timeout for requests to the backend.
*   **`static_resources.clusters`**: Defines backend clusters.
    *   **`rs_vsdm2_cluster`**: Cluster for the `rs_vsdm2` server.
        *   `type: STRICT_DNS`: Uses DNS to resolve the backend address.
        *   `load_assignment.endpoints.address.address: rs-vsdm2-service`:  **Replace `rs-vsdm2-service` with the actual hostname or Kubernetes service name of your `rs_vsdm2` server.** If running locally, you might use `localhost`.
        *   `load_assignment.endpoints.address.port_value: 8080`: Port of the `rs_vsdm2` server.
    *   **`otel_collector_cluster`**: Cluster for the OpenTelemetry Collector.
        *   `type: STRICT_DNS`: Uses DNS to resolve the collector address.
        *   `http2_protocol_options: {}`: Enables HTTP/2 for gRPC communication with the collector.
        *   `load_assignment.endpoints.address.address: otel-collector-service`: **Replace `otel-collector-service` with the actual hostname or Kubernetes service name of your OpenTelemetry Collector.** If running locally, you might use `localhost`.
        *   `load_assignment.endpoints.address.port_value: 4317`: OTLP gRPC port of the collector.
*   **`tracing.http`**: Defines the global tracing configuration.
    *   `name: envoy.tracers.opentelemetry`: Specifies the OpenTelemetry tracer.
    *   `typed_config.service_name: envoy-proxy-vsdm2-global`: Sets a global service name for traces.
    *   `typed_config.grpc_service.envoy_grpc.cluster_name: otel_collector_cluster`: Specifies the `otel_collector_cluster` to send traces to.
    *   `typed_config.context_export_sampled: true`: Exports sampled traces.
    *   `typed_config.context_export_unsampled: false`: Does not export unsampled traces (adjust as needed).
    *   `typed_config.resource_attributes`: Adds resource attributes to traces.
        *   `key: deployment.environment`, `value.string_value: "kubernetes"`: Example attribute to indicate the environment.

## Docker Compose

**To run Envoy with this configuration (using Docker Compose):**

1.  **Create `envoy.yaml`** in the same directory as `docker-compose.yaml`, `otel-collector-config.yaml`, `Dockerfile`, and `rs_vsdm2.go`.
2.  **Modify `docker-compose.yaml`** to include Envoy:

   ```yaml
   # docker-compose.yaml (modified)
   version: '3.8'
   services:
     rs_vsdm2_server:
       build: .
       ports:
         - "8080:8080"
       environment:
         OTLP_ENDPOINT: otel-collector:4317
       depends_on:
         - otel-collector

     otel-collector:
       image: otel/opentelemetry-collector-contrib:latest
       ports:
         - "4317:4317"
         - "4318:4318"
         - "8888:8888"
         - "8889:8889"
       volumes:
         - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
       command: ["--config=/etc/otel-collector-config.yaml", "--set=service.telemetry.logs.level=debug"]

     envoy-proxy: # New Envoy proxy service
       image: envoyproxy/envoy:v1.29-latest # Use a recent Envoy version
       ports:
         - "8081:8081" # Expose Envoy's listening port
       volumes:
         - ./envoy.yaml:/etc/envoy/envoy.yaml
       depends_on:
         - rs_vsdm2_server
         - otel-collector
   ```

3.  **Run with Docker Compose**: `docker-compose up --build`

Now, send requests to Envoy on port 8081 (`http://localhost:8081/vsdservice/v1/vsdmbundle`). Envoy will:

*   Receive the request.
*   Generate or propagate trace context (if `traceparent` is provided).
*   Forward the request to `rs_vsdm2_server` on port 8080.
*   Send traces to the OpenTelemetry Collector.
*   Return the response from `rs_vsdm2_server` back to the client.

**Important Notes:**

*   **Replace Placeholders**:  Remember to replace `rs-vsdm2-service` and `otel-collector-service` in `envoy.yaml` with the correct hostnames or service names based on your deployment environment (Kubernetes service names if deploying to Kubernetes, or `localhost` or container names if running locally with Docker Compose if services are in the same Docker network).
*   **Envoy Image Version**: Use a recent and stable Envoy image version (like `envoyproxy/envoy:v1.29-latest` or a more specific version) for best results and security.
*   **OTLP Collector Configuration**: Ensure your OpenTelemetry Collector is configured to receive and process OTLP gRPC traces on port 4317. The `otel-collector-config.yaml` provided earlier in this response shows a basic logging exporter. For real-world tracing, you'll want to configure a proper exporter (Jaeger, Zipkin, Tempo, etc.) in the collector configuration.
*   **Error Handling**: The Envoy configuration includes basic error handling (`status_on_error` in `opentelemetry_http` filter). You might need to add more robust error handling and retry policies in a production setup.
*   **Security**: This configuration is for demonstration purposes. For production, consider security aspects like TLS for communication between Envoy and backend services, access control for the admin interface, and securing the OTLP endpoint.
*   
## Kubernetes Deployment

```yaml
# envoy-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: envoy-config
data:
  envoy.yaml: |
    admin:
      access_log_path: /tmp/admin_access.log
      address:
        socket_address:
          protocol: TCP
          address: 0.0.0.0
          port_value: 9901

    static_resources:
      listeners:
        - name: listener_0
          address:
            socket_address:
              protocol: TCP
              address: 0.0.0.0
              port_value: 8081 # Envoy proxy listening port
          filter_chains:
            - filters:
              - name: envoy.filters.network.http_connection_manager
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                  stat_prefix: ingress_http
                  access_log:
                    - name: envoy.access_loggers.stdout
                      typed_config:
                        "@type": type.googleapis.com/envoy.extensions.access_loggers.stream.v3.StdoutAccessLog
                        format: "[%START_TIME%] \"%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%\" %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% %RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)% [%UPSTREAM_CLUSTER%] [%UPSTREAM_HOST%] [%REQ(X-REQUEST-ID)%] trace_id=%TRACE_ID% span_id=%SPAN_ID% parent_span_id=%PARENT_SPAN_ID%\n"
                  http_filters:
                    - name: envoy.filters.http.opentelemetry_http
                      typed_config:
                        "@type": type.googleapis.com/envoy.extensions.filters.http.opentelemetry.v3.OpenTelemetryConfig
                        service_name: envoy-proxy-vsdm2
                        emit_attributes_as_spans: true
                        status_on_error:
                          code: 500
                        grpc_service:
                          envoy_grpc:
                            cluster_name: otel_collector_cluster
                            initial_metadata: []
                    - name: envoy.filters.http.router
                      typed_config:
                        "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
                  route_config:
                    name: local_route
                    virtual_hosts:
                      - name: local_service
                        domains: ["*"]
                        routes:
                          - match:
                              prefix: "/" # Route all requests
                            route:
                              cluster: rs_vsdm2_cluster
                              timeout: 10s # Example timeout

      clusters:
        - name: rs_vsdm2_cluster
          connect_timeout: 0.25s
          type: STRICT_DNS
          lb_policy: ROUND_ROBIN
          load_assignment:
            cluster_name: rs_vsdm2_cluster
            endpoints:
              - lb_endpoints:
                  - endpoint:
                      address:
                        socket_address:
                          address: rs-vsdm2-service # Kubernetes service name of rs_vsdm2 server
                          port_value: 8080 # Port of rs_vsdm2 server

        - name: otel_collector_cluster
          connect_timeout: 0.25s
          type: STRICT_DNS
          lb_policy: ROUND_ROBIN
          http2_protocol_options: {} # Required for gRPC
          load_assignment:
            cluster_name: otel_collector_cluster
            endpoints:
              - lb_endpoints:
                  - endpoint:
                      address:
                        socket_address:
                          address: otel-collector-service # Kubernetes service name of otel-collector
                          port_value: 4317 # OTLP gRPC port

    tracing:
      http:
        name: envoy.tracers.opentelemetry
        typed_config:
          "@type": type.googleapis.com/envoy.config.trace.v3.OpenTelemetryConfig
          service_name: envoy-proxy-vsdm2-global # Global tracer service name
          grpc_service:
            envoy_grpc:
              cluster_name: otel_collector_cluster
              initial_metadata: []
          context_export_sampled: true # Export even sampled traces
          context_export_unsampled: false # Don't export unsampled traces (adjust as needed)
          resource_attributes:
            - key: deployment.environment
              value:
                string_value: "kubernetes" # Example environment attribute
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: envoy-proxy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: envoy-proxy
  template:
    metadata:
      labels:
        app: envoy-proxy
    spec:
      containers:
        - name: envoy-proxy
          image: envoyproxy/envoy:v1.29-latest # Use a recent Envoy version
          ports:
            - containerPort: 8081 # Envoy listening port
          volumeMounts:
            - name: envoy-config-volume
              mountPath: /etc/envoy/envoy.yaml
              subPath: envoy.yaml
      volumes:
        - name: envoy-config-volume
          configMap:
            name: envoy-config
---
apiVersion: v1
kind: Service
metadata:
  name: envoy-proxy-service
spec:
  selector:
    app: envoy-proxy
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
  type: LoadBalancer # Or ClusterIP if you only need internal access
```

**Explanation of Kubernetes Manifests for Envoy Proxy:**

*   **`envoy-configmap.yaml`**:
    *   `apiVersion: v1`, `kind: ConfigMap`: Defines a ConfigMap resource.
    *   `metadata.name: envoy-config`: Names the ConfigMap `envoy-config`.
    *   `data.envoy.yaml`: Contains the Envoy configuration from the previous step, stored as a string under the key `envoy.yaml`. This is the same `envoy.yaml` file we used in Docker Compose.

*   **`envoy-deployment.yaml`**:
    *   `apiVersion: apps/v1`, `kind: Deployment`: Defines a Deployment resource.
    *   `metadata.name: envoy-proxy`: Names the Deployment `envoy-proxy`.
    *   `spec.replicas: 1`: Runs a single replica of the Envoy proxy. Adjust as needed for your desired availability.
    *   `spec.selector.matchLabels.app: envoy-proxy`: Selector to match pods managed by this Deployment.
    *   `spec.template.metadata.labels.app: envoy-proxy`: Labels applied to the pods created by this Deployment.
    *   `spec.template.spec.containers`: Defines the container specification for the Envoy proxy pod.
        *   `containers.name: envoy-proxy`: Names the container `envoy-proxy`.
        *   `containers.image: envoyproxy/envoy:v1.29-latest`: Uses the same Envoy image as in the Docker Compose example. **Ensure you use a stable and recent version.**
        *   `containers.ports.containerPort: 8081`: Exposes port 8081 inside the container, which is where Envoy is listening.
        *   `containers.volumeMounts`: Mounts the `envoy-config` ConfigMap as a volume.
            *   `mountPath: /etc/envoy/envoy.yaml`: Mounts the ConfigMap content to the `/etc/envoy/envoy.yaml` path inside the container.
            *   `subPath: envoy.yaml`: Specifies that only the `envoy.yaml` key from the ConfigMap should be mounted to this path.
        *   `spec.template.spec.volumes`: Defines volumes used by the pod.
            *   `volumes.name: envoy-config-volume`: Names the volume `envoy-config-volume`.
            *   `volumes.configMap.name: envoy-config`: Specifies that this volume is backed by the `envoy-config` ConfigMap.

*   **`envoy-service.yaml`**:
    *   `apiVersion: v1`, `kind: Service`: Defines a Service resource.
    *   `metadata.name: envoy-proxy-service`: Names the Service `envoy-proxy-service`.
    *   `spec.selector.app: envoy-proxy`: Selector to match pods for this Service (Envoy proxy pods).
    *   `spec.ports`: Defines the port mapping for the service.
        *   `ports.protocol: TCP`, `ports.port: 8081`, `ports.targetPort: 8081`: Exposes port 8081 of the service, forwarding traffic to port 8081 of the Envoy proxy pods.
    *   `spec.type: LoadBalancer`: Creates a LoadBalancer service. This is suitable if you want to expose the Envoy proxy externally. If you only need internal access within the Kubernetes cluster, you can change this to `ClusterIP`.

**To deploy Envoy Proxy to Kubernetes:**

1.  **Apply the Kubernetes manifests:**
    ```bash
    kubectl apply -f envoy-configmap.yaml
    kubectl apply -f envoy-deployment.yaml
    kubectl apply -f envoy-service.yaml
    ```
    Run these commands from the directory where you saved the manifest files.

After applying these manifests, the Envoy proxy will be deployed to your Kubernetes cluster. You can access it via the `envoy-proxy-service`. If you used `type: LoadBalancer`, Kubernetes will provision an external IP address for the service, and you can send requests to that IP on port 8081 to reach your `rs_vsdm2` server through the Envoy proxy with OpenTelemetry tracing enabled.
