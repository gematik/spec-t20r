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

// Define data structures based on the OpenAPI spec (simplified for example)
type GetVSDMBundleResponse struct {
	VSDMBundle VSDMBundle `json:"VSDMBundle"`
}

type VSDMBundle struct {
	ResourceType string `json:"resourceType"` // Minimal example
	// Add other fields as needed based on the OpenAPI spec
}

// Initialize tracer provider for OpenTelemetry
func initTracer() *sdktrace.TracerProvider {
	ctx := context.Background()

	// Get OTLP exporter endpoint from environment variable
	otlpEndpoint := os.Getenv("OTLP_ENDPOINT")
	if otlpEndpoint == "" {
		otlpEndpoint = "localhost:4317" // Default OTLP endpoint
		log.Printf("OTLP_ENDPOINT environment variable not set, using default: %s", otlpEndpoint)
	} else {
		log.Printf("Using OTLP_ENDPOINT from environment variable: %s", otlpEndpoint)
	}

	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(otlpEndpoint),
		otlptracegrpc.WithInsecure(), // For local development, disable security
	)
	if err != nil {
		log.Fatalf("Failed to create exporter: %v", err)
	}

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName("rs_vsdm2"),
			semconv.ServiceVersion("1.0.0"),
			attribute.String("environment", "development"), // Or get from env var
		),
	)
	if err != nil {
		log.Fatalf("Failed to create resource: %v", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()), // Sample all traces for this example
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{}) // Use TraceContext for propagation

	return tp
}

func getVSDMBundleHandler(tracer trace.Tracer) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx := r.Context()

		// Extract traceparent from headers
		carrier := propagation.HeaderCarrier(r.Header)
		ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

		// Start a new span
		ctx, span := tracer.Start(ctx, "getVSDMBundle", trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		span.SetAttributes(semconv.HTTPMethod(r.Method))
		span.SetAttributes(semconv.HTTPRoute("/vsdservice/v1/vsdmbundle"))

		// Simulate API logic - replace with actual VSDMBundle retrieval
		response := GetVSDMBundleResponse{
			VSDMBundle: VSDMBundle{
				ResourceType: "Bundle",
				// ... more realistic data here if needed
			},
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK) // 200 OK

		enc := json.NewEncoder(w)
		if err := enc.Encode(response); err != nil {
			span.RecordError(err)
			span.SetAttributes(semconv.HTTPStatusCode(http.StatusInternalServerError))
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			log.Printf("Error encoding JSON: %v", err)
			return
		}

		span.SetAttributes(semconv.HTTPStatusCode(http.StatusOK))
		log.Println("Successfully served /vsdservice/v1/vsdmbundle")
	}
}

func main() {
	tp := initTracer()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Fatalf("TracerProvider shutdown failed: %v", err)
		}
	}()

	tracer := otel.Tracer("rs_vsdm2")

	mux := http.NewServeMux()
	mux.HandleFunc("/vsdservice/v1/vsdmbundle", getVSDMBundleHandler(tracer))

	port := ":8080"
	log.Printf("Server listening on port %s", port)
	server := &http.Server{
		Addr:         port,
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
