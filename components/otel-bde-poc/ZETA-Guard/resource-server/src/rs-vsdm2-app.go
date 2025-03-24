package main

import (
	"context"
	"encoding/json"
	"flag"
	stdlog "log" // Umbenennen des Standard-Log-Pakets
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	sdklog "go.opentelemetry.io/otel/sdk/log"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
	"go.opentelemetry.io/otel/trace"

	"go.opentelemetry.io/contrib/bridges/otelslog"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
	"go.opentelemetry.io/otel/log/global"
	"go.opentelemetry.io/otel/metric"
)

// ... (Strukturdefinitionen bleiben gleich) ...
type GetVSDMBundleResponse struct {
	VSDMBundle VSDMBundle `json:"VSDMBundle"`
}

type VSDMBundle struct {
	ResourceType string     `json:"resourceType"`
	Id           string     `json:"id"`
	Meta         Meta       `json:"meta"`
	Identifier   Identifier `json:"identifier"`
	Type         string     `json:"type"`
	Timestamp    string     `json:"timestamp"`
	Total        int        `json:"total"`
	Link         []Link     `json:"link"`
	Entry        []Entry    `json:"entry"`
}

type Meta struct {
	Profile []string `json:"profile"`
}

type Identifier struct {
	System string `json:"system"`
	Value  string `json:"value"`
}

type Link struct {
	Relation string `json:"relation"`
	Url      string `json:"url"`
}

type Entry struct {
	FullUrl  string   `json:"fullUrl"`
	Resource Resource `json:"resource"`
}

type Resource struct {
	ResourceType string       `json:"resourceType"`
	Id           string       `json:"id,omitempty"`
	Meta         *Meta        `json:"meta,omitempty"`
	Identifier   []Identifier `json:"identifier,omitempty"`
	Status       string       `json:"status,omitempty"`
	Type         *Type        `json:"type,omitempty"`
	SubscriberId string       `json:"subscriberId,omitempty"`
	Beneficiary  *Reference   `json:"beneficiary,omitempty"`
	Payor        []Reference  `json:"payor,omitempty"`
	Period       *Period      `json:"period,omitempty"`
	Name         []Name       `json:"name,omitempty"`
	Gender       string       `json:"gender,omitempty"`
	BirthDate    string       `json:"birthDate,omitempty"`
}

type Type struct {
	Coding []Coding `json:"coding"`
}

type Coding struct {
	System  string `json:"system"`
	Code    string `json:"code"`
	Display string `json:"display"`
}

type Reference struct {
	Reference string `json:"reference"`
}

type Period struct {
	Start string `json:"start"`
}

type Name struct {
	Family string   `json:"family"`
	Given  []string `json:"given"`
}

// SiemEvent Strukturdefinition
type SiemEvent struct {
	CustomerID           string   `json:"customer_id"`
	Title                string   `json:"title"`
	Description          string   `json:"description"`
	Severity             string   `json:"severity"`
	Status               string   `json:"status"`
	Environment          string   `json:"environment"`
	Date                 string   `json:"date"`
	Host                 string   `json:"host"`
	IP                   string   `json:"ip"`
	CaseID               int      `json:"case_id"`
	Category             string   `json:"category"`
	MitreAttackTactic    []string `json:"mitre_attack_tactic"`
	MitreAttackTechnique []string `json:"mitre_attack_technique"`
	Product              string   `json:"product"`
	Reference            []string `json:"reference"`
	Disposition          string   `json:"Disposition"`
	DispositionComment   string   `json:"disposition_comment"`
	PodName              string   `json:"pod_name"`
	Timestamp            string   `json:"timestamp"`
}

// Konstanten für Produktinformationen und Konfiguration
const (
	productName          = "rs-vsdm2-app"
	productVersion       = "1.0.1"
	productTypeVersion   = "VSDM2"
	configurationVersion = "1.0"
)

var (
	otel_tracer = otel.Tracer(productName)
	otel_meter  = otel.Meter(productName)
	otel_logger = otelslog.NewLogger(productName)
	rollCnt     metric.Int64Counter
	debugMode   bool
	ctx         = context.Background()
)

func initTelemetry() (*sdktrace.TracerProvider, *sdklog.LoggerProvider) {
	otlpEndpoint := os.Getenv("OTLP_ENDPOINT")
	if otlpEndpoint == "" {
		otlpEndpoint = "localhost:4317"
		stdlog.Printf("[WARN] OTLP_ENDPOINT not set, using default: %s", otlpEndpoint)
	}

	if debugMode {
		stdlog.Printf("[DEBUG] OTLP Exporter sending to: %s", otlpEndpoint)
	}

	// Erstellen eines gemeinsamen Resource-Objekts
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName(productName),
			semconv.ServiceVersion(productVersion),
			attribute.String("environment", "development"),
		),
	)
	if err != nil {
		stdlog.Fatalf("[ERROR] Failed to create OpenTelemetry resource: %v", err)
	}

	// Trace Exporter setup
	traceExporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(otlpEndpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		stdlog.Fatalf("[ERROR] Failed to create OTLP trace exporter: %v", err)
	}

	// Trace Provider
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(traceExporter),
		sdktrace.WithResource(res),
	)

	// Logs Exporter setup
	logExporter, err := otlploggrpc.New(ctx,
		otlploggrpc.WithEndpoint(otlpEndpoint),
		otlploggrpc.WithInsecure(),
	)
	if err != nil {
		stdlog.Fatalf("[ERROR] Failed to create OTLP log exporter: %v", err)
	}

	// Logs Provider
	lp := sdklog.NewLoggerProvider(
		sdklog.WithResource(res),
		sdklog.WithProcessor(sdklog.NewBatchProcessor(logExporter)),
	)

	otel.SetTracerProvider(tp)
	//otel.SetLogger(lp) // SetLogger configures the logger used internally to opentelemetry.
	global.SetLoggerProvider(lp) // Logger Provider global setzen
	defer func() {
		if err := lp.Shutdown(ctx); err != nil {
			panic(err)
		}
	}()

	otel.SetTextMapPropagator(propagation.TraceContext{})

	stdlog.Println("[INFO] OpenTelemetry tracer and logger initialized successfully")
	return tp, lp
}

func logProductInfo() {
	podName := os.Getenv("POD_NAME")
	if podName == "" {
		podName = "unknown"
	}

	productInfo := []attribute.KeyValue{
		attribute.String("product.name", productName),
		attribute.String("product.version", productVersion),
		attribute.String("producttype.version", productTypeVersion),
		attribute.String("configuration.version", configurationVersion),
		attribute.String("pod.name", podName),
		attribute.String("timestamp", time.Now().Format(time.RFC3339)),
	}

	eventJSON, err := json.Marshal(productInfo)
	if err != nil {
		stdlog.Printf("[ERROR] Failed to marshal product_info to JSON: %v", err)
		return
	}

	otel_logger.Info(string(eventJSON))
	stdlog.Println("[INFO] Product info log sent")
}

func getVSDMBundleHandler(tracer trace.Tracer) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		ctx := r.Context()
		stdlog.Printf("[INFO] Received request: %s %s", r.Method, r.URL.Path)

		if debugMode {
			stdlog.Println("[DEBUG] Request Headers:")
			for name, headers := range r.Header {
				for _, h := range headers {
					stdlog.Printf("[DEBUG]     %v: %v", name, h)
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
			stdlog.Printf("[WARN] Failed to parse RemoteAddr: %v", err)
		}

		response := GetVSDMBundleResponse{
			VSDMBundle: VSDMBundle{
				ResourceType: "Bundle",
				Id:           "example-vsdmbundle-1",
				Meta: Meta{
					Profile: []string{"https://gematik.de/fhir/vsdm2/StructureDefinition/VSDMBundle"},
				},
				Identifier: Identifier{
					System: "urn:ietf:rfc:3986",
					Value:  "urn:uuid:a1b2c3d4-e5f6-7890-1234-567890abcdef",
				},
				Type:      "collection",
				Timestamp: "2023-10-27T10:00:00Z",
				Total:     3,
				Link: []Link{
					{
						Relation: "self",
						Url:      "https://example.com/fhir/VSDMBundle/example-vsdmbundle-1",
					},
				},
				Entry: []Entry{
					{
						FullUrl: "urn:uuid:patient-example-1",
						Resource: Resource{
							ResourceType: "Patient",
							Id:           "patient-example-1",
							Meta: &Meta{
								Profile: []string{"https://gematik.de/fhir/vsdm2/StructureDefinition/VSDPatient"},
							},
							Identifier: []Identifier{
								{
									System: "urn:oid:1.2.276.0.76.4.512",
									Value:  "123456789",
								},
							},
							Name: []Name{
								{
									Family: "Mustermann",
									Given:  []string{"Max"},
								},
							},
							Gender:    "male",
							BirthDate: "1970-01-01",
						},
					},
					{
						FullUrl: "urn:uuid:coverage-example-1",
						Resource: Resource{
							ResourceType: "Coverage",
							Id:           "coverage-example-1",
							Meta: &Meta{
								Profile: []string{"https://gematik.de/fhir/vsdm2/StructureDefinition/VSDMCoverage"},
							},
							Status: "active",
							Type: &Type{
								Coding: []Coding{
									{
										System:  "http://terminology.hl7.org/CodeSystem/v3-ActCode",
										Code:    "EHCPOL",
										Display: "extended healthcare policy",
									},
								},
							},
							SubscriberId: "KV123456789",
							Beneficiary: &Reference{
								Reference: "urn:uuid:patient-example-1",
							},
							Payor: []Reference{
								{
									Reference: "urn:uuid:organization-example-1",
								},
							},
							Period: &Period{
								Start: "2023-01-01",
							},
						},
					},
					{
						FullUrl: "urn:uuid:organization-example-1",
						Resource: Resource{
							ResourceType: "Organization",
							Id:           "organization-example-1",
							Meta: &Meta{
								Profile: []string{"https://gematik.de/fhir/vsdm2/StructureDefinition/VSDMOrganization"},
							},
							Identifier: []Identifier{
								{
									System: "urn:oid:1.2.276.0.76.4.511",
									Value:  "ORG12345",
								},
							},
							Name: []Name{
								{
									Family: "Beispiel Krankenkasse",
									Given:  []string{},
								},
							},
						},
					},
				},
			}}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		if debugMode {
			stdlog.Println("[DEBUG] Response Body (JSON):")
			responseBytes, err := json.MarshalIndent(response, "", "  ")
			if err != nil {
				stdlog.Printf("[ERROR] Failed to marshal response for debug logging: %v", err)
			} else {
				stdlog.Println(string(responseBytes))
			}
		}

		enc := json.NewEncoder(w)
		if err := enc.Encode(response); err != nil {
			stdlog.Printf("[ERROR] JSON encoding failed: %v", err)
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

		stdlog.Printf("[INFO] Served /vsdservice/v1/vsdmbundle in %v", duration)
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

func getLocalIP() string {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return "unknown"
	}
	for _, addr := range addrs {
		if ipnet, ok := addr.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
			if ipnet.IP.To4() != nil {
				return ipnet.IP.String()
			}
		}
	}
	return "unknown"
}

// func logSiemEvent(logger log.Logger) { // Verwende otel/log.Logger
func logSiemEvent() { // Verwende global lp.Logger
	hostname, _ := os.Hostname()
	currentDate := time.Now().Format("2006-01-02")
	localIP := getLocalIP()
	podName := os.Getenv("POD_NAME")
	if podName == "" {
		podName = "unknown"
	}
	currentTime := time.Now().Format(time.RFC3339)

	siemEvent := SiemEvent{
		CustomerID:           "289347a29038534df52352t34112",
		Title:                "use_case_name",
		Description:          "several incorrect login attempts to the system detected",
		Severity:             "WARN",
		Status:               "Open",
		Environment:          "pu",
		Date:                 currentDate,
		Host:                 hostname,
		IP:                   localIP,
		CaseID:               2323,
		Category:             "security-alert",
		MitreAttackTactic:    []string{},
		MitreAttackTechnique: []string{},
		Product:              "TI-Gateway",
		Reference:            []string{"https://www.tenable.com/plugins/nessus/182691"},
		Disposition:          "false-positive",
		DispositionComment:   "user has entered his password incorrectly because caps lock was activated",
		PodName:              podName,
		Timestamp:            currentTime,
	}

	eventJSON, err := json.Marshal(siemEvent)
	if err != nil {
		stdlog.Printf("[ERROR] Failed to marshal siem_event to JSON: %v", err)
		return
	}

	otel_logger.Warn(string(eventJSON)) // Verwenden Sie logger.Info direkt mit Attributen
	//logger.InfoContext(ctx, "Siem event", attrs...) // Verwenden Sie logger.Warn direkt mit Attributen
	stdlog.Println("[INFO] Siem event log sent")
}

func main() {
	stdlog.Println("[INFO] Starting rs-vsdm2-app service...")

	flag.BoolVar(&debugMode, "debug", false, "Enable debug logging")
	flag.Parse()

	if debugMode {
		stdlog.Println("[DEBUG] Debug mode is enabled")
	}

	tp, lp := initTelemetry()
	defer func() {
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := tp.Shutdown(shutdownCtx); err != nil {
			stdlog.Fatalf("[ERROR] TracerProvider shutdown failed: %v", err)
		}
		if err := lp.Shutdown(shutdownCtx); err != nil {
			stdlog.Fatalf("[ERROR] LoggerProvider shutdown failed: %v", err)
		}
		stdlog.Println("[INFO] TracerProvider and LoggerProvider shut down successfully")
	}()

	mux := http.NewServeMux()
	mux.HandleFunc("/vsdservice/v1/vsdmbundle", getVSDMBundleHandler(otel_tracer))

	port := ":8080"
	stdlog.Printf("[INFO] Server listening on port %s", port)

	server := &http.Server{
		Addr:         port,
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			stdlog.Fatalf("[ERROR] Server failed to start: %v", err)
		}
	}()

	// Sende Produkt-Info-Log mit dem Logger Provider
	logProductInfo()

	// Sende Siem Event Log jede Minute
	go func() {
		ticker := time.NewTicker(1 * time.Minute)
		defer ticker.Stop()
		for range ticker.C {
			logSiemEvent()
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	<-stop
	stdlog.Println("[INFO] Shutting down server...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		stdlog.Fatalf("[ERROR] Server forced to shutdown: %v", err)
	}

	stdlog.Println("[INFO] Server exited cleanly")
}
