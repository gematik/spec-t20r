# rs_vsdm2

The `rs_vsdm2` server is a simple Go server that implements the `/vsdservice/v1/vsdmbundle` endpoint from the VSDM API. This server is designed to be used as a resource server in the VSDM reference architecture, providing a basic implementation of the VSDM API endpoint for retrieving a VSDM bundle. The server includes support for OpenTelemetry tracing, allowing it to create and propagate trace contexts using the `traceparent` header.

**To run this server:**

1.  **Install dependencies:**
    ```bash
    go mod init rs_vsdm2
    go get go.opentelemetry.io/otel
    go get go.opentelemetry.io/otel/trace
    go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc
    go get go.opentelemetry.io/otel/sdk/trace
    go get go.opentelemetry.io/otel/propagation
    go get go.opentelemetry.io/otel/sdk/resource
    go get go.opentelemetry.io/otel/semconv/v1.21.0
    ```

2.  **Set the `OTLP_ENDPOINT` environment variable** to point to your OpenTelemetry Collector. For example, if your collector is running locally on the default gRPC port:
    ```bash
    export OTLP_ENDPOINT="localhost:4317"
    ```
    If you are using Docker, ensure your Go application and the Collector can communicate over the network.

3.  **Run the Go server:**
    ```bash
    go run rs_vsdm2.go
    ```

4.  **Send a request to the server:**
    You can use `curl` or any HTTP client to send a GET request:
    ```bash
    curl http://localhost:8080/vsdservice/v1/vsdmbundle
    ```

    To simulate a request from a proxy with a `traceparent` header, you can add the header to your curl request:
    ```bash
    curl -H "traceparent: 00-your-trace-id-your-span-id-01" http://localhost:8080/vsdservice/v1/vsdmbundle
    ```
    Replace `your-trace-id` and `your-span-id` with valid trace and span IDs if you want to join an existing trace. If you don't provide a `traceparent`, a new trace will be started.

5.  **Observe traces in your OpenTelemetry Collector and backend:**
    After sending requests, you should see traces in your configured OpenTelemetry backend (like Jaeger, Zipkin, or a cloud observability platform), showing the spans created by the `rs_vsdm2` server, including the propagated context if you sent a `traceparent` header.

**Explanation:**

*   **`initTracer()`:**
    *   Reads the `OTLP_ENDPOINT` from the environment variable.
    *   Creates an OTLP gRPC exporter to send traces to the collector.
    *   Creates a resource describing the service.
    *   Creates a `TracerProvider` that samples all traces and batches them for export.
    *   Sets the global TracerProvider and TextMapPropagator.
*   **`getVSDMBundleHandler()`:**
    *   Extracts the `traceparent` header from the incoming request using `otel.GetTextMapPropagator().Extract()`. This ensures that if a trace context is present in the incoming request (from the proxy), it's correctly propagated.
    *   Starts a new span using `tracer.Start()` with the extracted context, creating a child span if a `traceparent` was present, or a new root span if not.
    *   Sets semantic attributes for HTTP method and route on the span.
    *   Simulates the API logic (returning a minimal `VSDMBundleResponse`).
    *   Encodes the response as JSON and writes it to the `ResponseWriter`.
    *   Sets semantic attributes for the HTTP status code on the span.
    *   Handles potential JSON encoding errors and server errors, recording errors on the span and setting appropriate HTTP status codes.
*   **`main()`:**
    *   Initializes the tracer provider using `initTracer()`.
    *   Sets up HTTP routing using `http.NewServeMux()`.
    *   Registers the `getVSDMBundleHandler` for the `/vsdservice/v1/vsdmbundle` path.
    *   Starts the HTTP server on port 8080.
    *   Includes a `defer` function to shut down the `TracerProvider` gracefully when the application exits, ensuring that pending traces are exported.

This is a basic server that implements the vsdm2 endpoint and supports OpenTelemetry tracing, including propagation of the `traceparent` header. You can expand this server by implementing the full API logic, data validation, and more detailed error handling as needed based on the complete OpenAPI specification and your application requirements.

## Docker support

**Dockerfile**

```dockerfile
# Dockerfile for rs_vsdm2 Go server

# Builder stage: Compile the Go application
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum to download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the application
RUN go build -o rs_vsdm2 ./rs_vsdm2.go

# Runtime stage: Create a minimal image to run the application
FROM alpine:latest

WORKDIR /app

# Copy the executable from the builder stage
COPY --from=builder /app/rs_vsdm2 /app/rs_vsdm2

# Expose the port the app listens on
EXPOSE 8080

# Command to run the executable
CMD ["./rs_vsdm2"]
```

**Explanation:**

1.  **`FROM golang:1.22-alpine AS builder`**:
    *   This line starts the first stage of the multi-stage build, using the official `golang:1.22-alpine` image as the base. This image is based on Alpine Linux and includes Go 1.22, making it suitable for building Go applications.
    *   `AS builder` names this stage "builder", allowing us to refer to it in later stages.

2.  **`WORKDIR /app`**:
    *   Sets the working directory inside the container to `/app`. All subsequent commands will be executed in this directory.

3.  **`COPY go.mod go.sum ./`**:
    *   Copies the `go.mod` and `go.sum` files from the host machine (in the same directory as the Dockerfile) to the `/app` directory in the container.
    *   These files are necessary for Go's dependency management.

4.  **`RUN go mod download`**:
    *   Executes the `go mod download` command. This command reads the `go.mod` and `go.sum` files and downloads all the Go dependencies required by the application.
    *   By copying `go.mod` and `go.sum` first and downloading dependencies before copying the entire source code, Docker can cache this layer. This speeds up subsequent builds if only the source code changes.

5.  **`COPY . .`**:
    *   Copies all files and directories from the current directory on the host machine to the `/app` directory in the container. This includes the `rs_vsdm2.go` source file and any other necessary files.

6.  **`RUN go build -o rs_vsdm2 ./rs_vsdm2.go`**:
    *   Builds the Go application.
    *   `go build` is the Go command for compiling Go source code.
    *   `-o rs_vsdm2` specifies the output executable file name as `rs_vsdm2`.
    *   `./rs_vsdm2.go` specifies the source file to build.

7.  **`FROM alpine:latest`**:
    *   Starts the second stage, the runtime stage, using the `alpine:latest` image. Alpine is a very small and lightweight Linux distribution, ideal for creating small container images.

8.  **`WORKDIR /app`**:
    *   Sets the working directory in the runtime stage to `/app`.

9.  **`COPY --from=builder /app/rs_vsdm2 /app/rs_vsdm2`**:
    *   Copies the compiled executable `rs_vsdm2` from the "builder" stage to the `/app` directory in the current (runtime) stage.
    *   `--from=builder` specifies that we are copying from the "builder" stage.

10. **`EXPOSE 8080`**:
    *   Declares that the container will listen on port 8080. This is informative and documents the port, but it doesn't actually publish the port. You need to use the `-p` flag when running the Docker container to publish the port to the host.

11. **`CMD ["./rs_vsdm2"]`**:
    *   Specifies the command to run when the container starts. In this case, it runs the compiled executable `./rs_vsdm2`.

**How to build and run the Docker image:**

1.  **Save the Dockerfile:** Save the above Dockerfile as `Dockerfile` in the same directory as your `rs_vsdm2.go` file, `go.mod`, and `go.sum`.
2.  **Build the Docker image:**
    ```bash
    docker build -t rs_vsdm2-server .
    ```
    *   `docker build` is the command to build a Docker image.
    *   `-t rs_vsdm2-server` tags the image with the name `rs_vsdm2-server`. You can choose a different name if you prefer.
    *   `.` specifies that the Dockerfile is in the current directory.

3.  **Run the Docker container:**
    ```bash
    docker run -p 8080:8080 -e OTLP_ENDPOINT="your-otlp-collector:4317" rs_vsdm2-server
    ```
    *   `docker run` is the command to run a Docker container.
    *   `-p 8080:8080` maps port 8080 of the host machine to port 8080 of the container. This makes the server accessible on `http://localhost:8080` (or your machine's IP address).
    *   `-e OTLP_ENDPOINT="your-otlp-collector:4317"` sets the `OTLP_ENDPOINT` environment variable inside the container. Replace `"your-otlp-collector:4317"` with the actual address of your OpenTelemetry Collector. If your collector is running on the same machine as Docker, you might use `host.docker.internal:4317` or the IP address of your host machine. If you are running the collector in a different Docker container, you might need to use Docker networking to allow communication. If you are running the collector locally on the default port, you can also use `localhost:4317` or simply omit the `-e OTLP_ENDPOINT` flag to use the default value in the Go code.
    *   `rs_vsdm2-server` is the name of the Docker image we built in the previous step.

Now your `rs_vsdm2` server should be running inside a Docker container, and you can access it at `http://localhost:8080`. Traces generated by the server will be sent to your OpenTelemetry Collector specified by the `OTLP_ENDPOINT` environment variable.

## docker-compose.yaml

```yaml
# docker-compose.yaml
version: '3.8'
services:
  rs_vsdm2_server:
    build: . # Assuming Dockerfile is in the same directory
    ports:
      - "8080:8080"
    environment:
      OTLP_ENDPOINT: otel-collector:4317 # Connect to otel-collector service
    depends_on:
      - otel-collector

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    ports:
      - "4317:4317" # OTLP gRPC
      - "4318:4318" # OTLP HTTP (optional, for other clients)
      - "8888:8888" # Prometheus metrics (optional)
      - "8889:8889" # Health check extension (optional)
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    command: ["--config=/etc/otel-collector-config.yaml", "--set=service.telemetry.logs.level=debug"]
```

**`otel-collector-config.yaml` (for docker-compose):**

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:

exporters:
  logging:
    loglevel: debug # Log traces to console for docker-compose example

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
```

**Explanation for `docker-compose.yaml` and `otel-collector-config.yaml`:**

*   **`docker-compose.yaml`**:
    *   **`rs_vsdm2_server` service**:
        *   `build: .`: Builds the Docker image using the `Dockerfile` in the current directory.
        *   `ports: - "8080:8080"`: Maps port 8080 of the host to port 8080 of the container.
        *   `environment: OTLP_ENDPOINT: otel-collector:4317`: Sets the `OTLP_ENDPOINT` environment variable for the server container to point to the `otel-collector` service on port 4317 (gRPC). Docker Compose automatically resolves service names to their container IPs.
        *   `depends_on: - otel-collector`: Ensures that the `otel-collector` service starts before the `rs_vsdm2_server`.
    *   **`otel-collector` service**:
        *   `image: otel/opentelemetry-collector-contrib:latest`: Uses the official OpenTelemetry Collector Contrib image, which includes a wide range of receivers, processors, and exporters.
        *   `ports`: Exposes ports for OTLP gRPC (4317), OTLP HTTP (4318), Prometheus metrics (8888), and health check (8889). You can adjust these as needed.
        *   `volumes: - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml`: Mounts the `otel-collector-config.yaml` file from the current directory into the container at `/etc/otel-collector-config.yaml`.
        *   `command`: Specifies the command to run when starting the collector container, using the mounted configuration file and setting the telemetry log level to debug for more verbose output.
*   **`otel-collector-config.yaml`**:
    *   **`receivers.otlp`**: Configures the OTLP receiver to listen on gRPC port 4317 on all interfaces (`0.0.0.0`).
    *   **`processors.batch`**: Adds a batch processor to improve efficiency by sending traces in batches.
    *   **`exporters.logging`**: Configures the logging exporter to output traces to the console. This is useful for local development and debugging with Docker Compose.
    *   **`service.pipelines.traces`**: Defines a trace pipeline that receives data from the `otlp` receiver, processes it with the `batch` processor, and exports it using the `logging` exporter.

**To run with Docker Compose:**

1.  Make sure you have Docker Compose installed.
2.  Create `docker-compose.yaml` and `otel-collector-config.yaml` in the same directory as your `Dockerfile` and `rs_vsdm2.go`.
3.  Run: `docker-compose up --build`

You should see logs from both the server and the collector in your terminal. Traces will be logged to the collector's console output.

---

## Kubernetes Deployment

**Kubernetes Manifests:**

Here are Kubernetes manifest files for deploying the server and OpenTelemetry Collector to Kubernetes.

**`rs-vsdm2-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rs-vsdm2-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rs-vsdm2-server
  template:
    metadata:
      labels:
        app: rs-vsdm2-server
    spec:
      containers:
        - name: rs-vsdm2-server
          image: rs_vsdm2-server # Replace with your Docker image name (after pushing to a registry)
          ports:
            - containerPort: 8080
          env:
            - name: OTLP_ENDPOINT
              value: otel-collector-service:4317 # Service name and port of otel-collector
```

**`rs-vsdm2-service.yaml`:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rs-vsdm2-service
spec:
  selector:
    app: rs-vsdm2-server
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: LoadBalancer # Or ClusterIP if you only need internal access
```

**`otel-collector-configmap.yaml`:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
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
      logging: # Replace with your desired exporter (e.g., otlp/jaeger, otlp/zipkin, otlp/tempo, etc.)
        loglevel: debug # Keep logging for Kubernetes example. For production, use a real exporter.

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [logging] # Replace with your desired exporter
```

**`otel-collector-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: otel-collector
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
            name: otel-collector-config
```

**`otel-collector-service.yaml`:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: otel-collector-service
spec:
  selector:
    app: otel-collector
  ports:
    - protocol: TCP
      port: 4317
      targetPort: 4317
  type: ClusterIP # Internal service, accessed by rs-vsdm2-server
```

**Explanation for Kubernetes Manifests:**

*   **`rs-vsdm2-deployment.yaml`**:
    *   Defines a Deployment for the `rs_vsdm2_server`.
    *   `image: rs_vsdm2-server`: **You need to replace `rs_vsdm2-server` with the actual name of your Docker image after you have built and pushed it to a container registry (like Docker Hub, Google Container Registry, AWS ECR, etc.).** Kubernetes needs to be able to pull this image.
    *   `env.OTLP_ENDPOINT: otel-collector-service:4317`: Sets the `OTLP_ENDPOINT` environment variable to point to the `otel-collector-service` (the Kubernetes Service name) on port 4317. Kubernetes DNS will resolve `otel-collector-service` to the internal cluster IP of the collector service.
*   **`rs-vsdm2-service.yaml`**:
    *   Defines a Service of type `LoadBalancer` (you can change it to `ClusterIP` if you only need internal access within the Kubernetes cluster).
    *   Exposes port 8080 of the Deployment as a service on port 8080.
*   **`otel-collector-configmap.yaml`**:
    *   Creates a ConfigMap named `otel-collector-config` to hold the collector configuration.
    *   The `data.otel-collector-config.yaml` section contains the same collector configuration as the `otel-collector-config.yaml` used in Docker Compose. **Important:** You should replace `exporters.logging` with a real exporter (e.g., to Jaeger, Zipkin, Tempo, or a cloud observability platform) for production deployments.
*   **`otel-collector-deployment.yaml`**:
    *   Defines a Deployment for the OpenTelemetry Collector.
    *   `image: otel/opentelemetry-collector-contrib:latest`: Uses the same collector image as in Docker Compose.
    *   `volumeMounts` and `volumes`: Mounts the `otel-collector-configmap.yaml` ConfigMap as a volume into the collector container, so the collector can use the configuration.
*   **`otel-collector-service.yaml`**:
    *   Defines a `ClusterIP` Service named `otel-collector-service` for the collector Deployment. `ClusterIP` is suitable because the `rs-vsdm2-server` will access the collector internally within the Kubernetes cluster.
    *   Exposes port 4317 of the collector Deployment as a service on port 4317.

**To deploy to Kubernetes:**

1.  **Build and push your Docker image:**
    ```bash
    docker build -t your-dockerhub-username/rs_vsdm2-server . # Replace with your Docker Hub username or registry
    docker push your-dockerhub-username/rs_vsdm2-server
    ```
    **Remember to replace `your-dockerhub-username/rs_vsdm2-server` in `rs-vsdm2-deployment.yaml` with the actual image name you pushed.**
2.  **Apply the Kubernetes manifests:**
    ```bash
    kubectl apply -f otel-collector-configmap.yaml
    kubectl apply -f otel-collector-deployment.yaml
    kubectl apply -f otel-collector-service.yaml
    kubectl apply -f rs-vsdm2-deployment.yaml
    kubectl apply -f rs-vsdm2-service.yaml
    ```
    Run these commands from the directory where you saved the manifest files.

After applying these manifests, your `rs-vsdm2-server` and OpenTelemetry Collector should be running in your Kubernetes cluster. You can access the server via the `rs-vsdm2-service` (if it's a `LoadBalancer`, you'll get an external IP). Traces will be sent to the collector, and in this example configuration, logged to the collector's logs (you can view collector logs using `kubectl logs deployment/otel-collector -n default`).

**Important Notes for Kubernetes Deployment:**

*   **Replace `exporters.logging`**: For a real Kubernetes deployment, you **must** replace the `exporters.logging` in `otel-collector-configmap.yaml` with a proper exporter that sends traces to a backend like Jaeger, Zipkin, Tempo, or a cloud observability platform. Configure the exporter settings according to your chosen backend.
*   **Image Registry**: Make sure your Kubernetes cluster can pull the Docker image you specified in `rs-vsdm2-deployment.yaml`. If you are using a private registry, you might need to configure image pull secrets in Kubernetes.
*   **Namespace**: These manifests are for the `default` namespace. You might want to deploy them to a different namespace in a production environment. If you do, ensure you create the namespace first and adjust the `metadata.namespace` in the manifests if needed.
*   **Resource Requests/Limits**: For production, you should add resource requests and limits to the container specifications in both Deployments to ensure resource management and stability.
*   **Service Type**: Choose the appropriate `Service` type (`LoadBalancer`, `ClusterIP`, `NodePort`, etc.) for `rs-vsdm2-service` based on how you want to expose your server. `LoadBalancer` is typically used for external access in cloud environments. `ClusterIP` is for internal access within the cluster.