// rs_vsdm2.go
package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
	"go.opentelemetry.io/otel/trace"
)

type GetVSDMBundleResponse struct {
	VSDMBundle VSDMBundle `json:"VSDMBundle"`
}

type VSDMBundle struct {
	ResourceType string `json:"resourceType"`
}

func initTracer() *sdktrace.TracerProvider {
	ctx := context.Background()

	otlpEndpoint := os.Getenv("OTLP_ENDPOINT")
	if otlpEndpoint == "" {
		otlpEndpoint = "localhost:4317"
		log.Printf("[WARN] OTLP_ENDPOINT environment variable not set, using default: %s", otlpEndpoint)
	} else {
		log.Printf("[INFO] Using OTLP_ENDPOINT: %s", otlpEndpoint)
	}

	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(otlpEndpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		log.Fatalf("[ERROR] Failed to create OTLP exporter: %v", err)
	}

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName("rs_vsdm2"),
			semconv.ServiceVersion("1.0.0"),
			attribute.String("environment", "development"),
		),
	)
	if err != nil {
		log.Fatalf("[ERROR] Failed to create OpenTelemetry resource: %v", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{})

	log.Println("[INFO] OpenTelemetry tracer initialized successfully")
	return tp
}

func getVSDMBundleHandler(tracer trace.Tracer) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		ctx := r.Context()

		log.Printf("[INFO] Received request: %s %s", r.Method, r.URL.Path)

		carrier := propagation.HeaderCarrier(r.Header)
		ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

		ctx, span := tracer.Start(ctx, "getVSDMBundle", trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		span.SetAttributes(semconv.HTTPMethod(r.Method))
		span.SetAttributes(semconv.HTTPRoute("/vsdservice/v1/vsdmbundle"))

		response := GetVSDMBundleResponse{
			VSDMBundle: VSDMBundle{
				ResourceType: "Bundle",
			},
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		enc := json.NewEncoder(w)
		if err := enc.Encode(response); err != nil {
			log.Printf("[ERROR] JSON encoding failed: %v", err)
			span.RecordError(err)
			span.SetAttributes(semconv.HTTPStatusCode(http.StatusInternalServerError))
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

		duration := time.Since(start)
		span.SetAttributes(semconv.HTTPStatusCode(http.StatusOK))
		log.Printf("[INFO] Successfully served /vsdservice/v1/vsdmbundle in %v", duration)
	}
}

func main() {
	log.Println("[INFO] Starting rs_vsdm2 service...")

	tp := initTracer()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Fatalf("[ERROR] TracerProvider shutdown failed: %v", err)
		}
		log.Println("[INFO] TracerProvider shut down successfully")
	}()

	tracer := otel.Tracer("rs_vsdm2")

	mux := http.NewServeMux()
	mux.HandleFunc("/vsdservice/v1/vsdmbundle", getVSDMBundleHandler(tracer))

	port := ":8080"
	log.Printf("[INFO] Server listening on port %s", port)

	server := &http.Server{
		Addr:         port,
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	// Start server and handle graceful shutdown
	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("[ERROR] Server failed to start: %v", err)
		}
	}()

	// Handle shutdown signal
	stop := make(chan os.Signal, 1)

	<-stop
	log.Println("[INFO] Shutting down server...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("[ERROR] Server forced to shutdown: %v", err)
	}

	log.Println("[INFO] Server exited cleanly")
}
