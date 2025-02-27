package main

import (
	"context"
	"encoding/json"
	"flag"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
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

var debugMode bool

func initTracer() *sdktrace.TracerProvider {
	ctx := context.Background()
	otlpEndpoint := os.Getenv("OTLP_ENDPOINT")
	if otlpEndpoint == "" {
		otlpEndpoint = "localhost:4317"
		log.Printf("[WARN] OTLP_ENDPOINT not set, using default: %s", otlpEndpoint)
	}

	if debugMode {
		log.Printf("[DEBUG] OTLP Exporter sending to: %s", otlpEndpoint)
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
			semconv.ServiceName("rs-vsdm2-app"),
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

		if debugMode {
			log.Println("[DEBUG] Request Headers:")
			for name, headers := range r.Header {
				for _, h := range headers {
					log.Printf("[DEBUG]     %v: %v", name, h)
				}
			}
		}

		carrier := propagation.HeaderCarrier(r.Header)
		ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

		ctx, span := tracer.Start(ctx, "rs-vsdm2-app.getVSDMBundle", trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		span.SetAttributes(
			semconv.HTTPMethodKey.String(r.Method),
			semconv.HTTPRouteKey.String("/vsdservice/v1/vsdmbundle"),
			semconv.HTTPTargetKey.String(r.URL.Path),
			semconv.HTTPRequestContentLengthKey.Int64(r.ContentLength),
		)

		host, port, err := net.SplitHostPort(r.RemoteAddr)
		if err == nil {
			span.SetAttributes(attribute.String("net.peer.ip", host))
			span.SetAttributes(attribute.String("net.host.port", port))
		} else {
			log.Printf("[WARN] Failed to parse RemoteAddr: %v", err)
		}

		response := GetVSDMBundleResponse{VSDMBundle: VSDMBundle{ResourceType: "Bundle"}}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		if debugMode {
			log.Println("[DEBUG] Response Body (JSON):")
			responseBytes, err := json.MarshalIndent(response, "", "  ")
			if err != nil {
				log.Printf("[ERROR] Failed to marshal response for debug logging: %v", err)
			} else {
				log.Println(string(responseBytes))
			}
		}

		enc := json.NewEncoder(w)
		if err := enc.Encode(response); err != nil {
			log.Printf("[ERROR] JSON encoding failed: %v", err)
			span.RecordError(err)
			span.SetAttributes(semconv.HTTPStatusCodeKey.Int(http.StatusInternalServerError))
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

		duration := time.Since(start)
		span.SetAttributes(semconv.HTTPStatusCodeKey.Int(http.StatusOK))

		respLen, err := getContentLength(response)
		if err == nil {
			span.SetAttributes(semconv.HTTPResponseContentLengthKey.Int64(int64(respLen)))
		}

		log.Printf("[INFO] Served /vsdservice/v1/vsdmbundle in %v", duration)
	}
}

// Berechnet die Länge der JSON-Antwort
func getContentLength(resp GetVSDMBundleResponse) (int, error) {
	responseBytes, err := json.Marshal(resp)
	if err != nil {
		return 0, err
	}
	return len(responseBytes), nil
}

func main() {
	log.Println("[INFO] Starting rs-vsdm2-app service...")

	flag.BoolVar(&debugMode, "debug", false, "Enable debug logging")
	flag.Parse()

	if debugMode {
		log.Println("[DEBUG] Debug mode is enabled")
	}

	tp := initTracer()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Fatalf("[ERROR] TracerProvider shutdown failed: %v", err)
		}
		log.Println("[INFO] TracerProvider shut down successfully")
	}()

	tracer := otel.Tracer("rs-vsdm2-app")

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

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("[ERROR] Server failed to start: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	<-stop
	log.Println("[INFO] Shutting down server...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("[ERROR] Server forced to shutdown: %v", err)
	}

	log.Println("[INFO] Server exited cleanly")
}
