# Open Telemetry

Siehe https://opentelemetry.io/

Das OpenTelemetry Protocol (OTLP) ist ein **allgemeines, herstellerunabhängiges Telemetrie-Datenübertragungsprotokoll**. Es wurde entwickelt, um die Art und Weise zu standardisieren, wie Telemetriedaten (wie Traces, Metriken und Logs) von Anwendungen und Infrastrukturkomponenten zu Backend-Systemen für Analyse und Beobachtung gesendet werden.

Hier sind die Hauptfunktionen von OTLP:

* **Standardisierung der Datenübertragung:** OTLP definiert ein einheitliches Datenmodell und Kodierungsformat für die Übertragung von Traces, Metriken und Logs. Dies beseitigt die Notwendigkeit, verschiedene proprietäre Protokolle zu verwenden und vereinfacht die Integration von Telemetriedaten in verschiedene Backend-Systeme.
* **Herstellerunabhängigkeit:** OTLP ist nicht an einen bestimmten Anbieter oder ein bestimmtes Produkt gebunden. Es kann mit verschiedenen Backend-Systemen verwendet werden, die OTLP unterstützen, wie z.B. Jaeger, Zipkin, Prometheus, Grafana und viele kommerzielle Observability-Plattformen.
* **Effizienz und Skalierbarkeit:** OTLP verwendet gRPC und Protocol Buffers für eine effiziente und performante Datenübertragung. Es ist für hohe Durchsatzraten und große Datenmengen ausgelegt und kann horizontal skaliert werden.
* **Einfache Integration:** OTLP wird von den OpenTelemetry SDKs in verschiedenen Programmiersprachen unterstützt. Dies erleichtert die Instrumentierung von Anwendungen und die Integration von OTLP in bestehende Systeme.
* **Transport Agnostisch:** OTLP selbst definiert nur das Datenmodell und die Kodierung. Es kann über verschiedene Transportprotokolle wie gRPC, HTTP/1.1 (in Zukunft HTTP/2 und HTTP/3) übertragen werden.

**Zusammenfassend lässt sich sagen, dass OTLP Folgendes macht:**

1. **Definiert ein standardisiertes Datenmodell** für die Darstellung von Traces, Metriken und Logs.
2. **Ermöglicht die Übertragung dieser Daten** von Anwendungen und Infrastrukturkomponenten zu Backend-Systemen.
3. **Vereinfacht die Integration** mit verschiedenen Observability-Tools und -Plattformen.
4. **Sorgt für eine effiziente und skalierbare Datenübertragung.**

**Vorteile von OTLP:**

* **Verbesserte Interoperabilität:** Verschiedene Tools und Systeme können nahtlos miteinander kommunizieren.
* **Geringere Komplexität:** Entwickler müssen sich nicht mit verschiedenen proprietären Protokollen auseinandersetzen.
* **Zukunftssicherheit:** OTLP ist ein offener Standard, der von einer großen Community unterstützt wird.
* **Flexibilität:** Unternehmen können die besten Tools für ihre Bedürfnisse wählen, ohne an einen bestimmten Anbieter gebunden zu sein.

**Kurz gesagt, OTLP ist ein wichtiger Bestandteil des OpenTelemetry-Ökosystems und spielt eine entscheidende Rolle bei der Standardisierung und Vereinfachung der Übertragung von Telemetriedaten für die Observability.**

OpenTelemetry kann den Versand von mehreren JSON-Objekten zusammenfassen und in einem bestimmten Intervall, wie z.B. alle 5 Minuten, versenden. Dies wird durch **Batching** und **Scheduling** erreicht.

Hier ist, wie es funktioniert:

**1. Batching (Zusammenfassung):**

* OpenTelemetry SDKs bieten in der Regel **Batch Processors** (z.B. `BatchSpanProcessor` für Traces, `BatchLogRecordProcessor` für Logs).
* Diese Processors sammeln Telemetriedaten (Spans, Log Records, etc.) im Speicher, anstatt sie sofort zu versenden.
* Sie konfigurieren den Batch Processor mit Parametern wie:
    * **`max_queue_size`:** Die maximale Anzahl von Telemetriedaten, die im Speicher gehalten werden können.
    * **`scheduled_delay_millis`:** Das Intervall (in Millisekunden), nach dem die gesammelten Daten versendet werden (z.B. 300000 für 5 Minuten).
    * **`export_timeout_millis`:** Die maximale Zeit, die für den Export eines Batches gewartet wird.
    * **`max_export_batch_size`:** Die maximale Anzahl von Telemetriedaten, die in einem einzelnen Exportvorgang gesendet werden. Wenn der Batch größer ist, wird er in mehrere Exporte aufgeteilt.

**2. Scheduling (Zeitgesteuerter Versand):**

* Der Batch Processor verwendet einen internen Timer, um den Versand der gesammelten Daten in regelmäßigen Abständen auszulösen.
* Basierend auf dem konfigurierten `scheduled_delay_millis` (z.B. 5 Minuten) wird der Batch Processor die Daten an den Exporter weiterleiten.

**3. Exporter (Versand):**

* Der Exporter ist verantwortlich für die eigentliche Übertragung der Daten an das Backend.
* OpenTelemetry bietet verschiedene Exporter, einschließlich eines OTLP Exporters, der die Daten im OTLP-Format (über gRPC oder HTTP) versenden kann.
* Es gibt auch Exporter, die Daten in anderen Formaten, wie z.B. JSON, versenden können. In diesem Fall würde der Exporter die gesammelten Telemetriedaten in eine Reihe von JSON-Objekten konvertieren und diese dann als einen Batch senden.

**Beispiel (vereinfachtes Konzept mit `BatchSpanProcessor` für Traces):**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter # Beispielhaft OTLP

# Konfiguration des Tracer Providers
trace.set_tracer_provider(TracerProvider())

# Konfiguration des OTLP Exporters
otlp_exporter = OTLPSpanExporter(endpoint="<your_collector_endpoint>")

# Konfiguration des BatchSpanProcessors (5 Minuten Intervall)
span_processor = BatchSpanProcessor(otlp_exporter, scheduled_delay_millis=300000, max_queue_size=2048, max_export_batch_size=512)

# Hinzufügen des Processors zum Tracer Provider
trace.get_tracer_provider().add_span_processor(span_processor)

# Jetzt werden alle erzeugten Spans vom BatchSpanProcessor gesammelt und alle 5 Minuten an den OTLP Exporter gesendet.
```

**Zusammenfassung:**

OpenTelemetry bietet durch die Kombination von Batch Processors und Exportern die Flexibilität, Telemetriedaten zu sammeln, zu bündeln und in einem gewünschten Intervall zu versenden. Obwohl OTLP selbst nicht direkt JSON verwendet, kann der Exporter die Daten in JSON konvertieren, bevor sie gesendet werden, falls das Backend dies erfordert. Die Konfiguration des Batching-Verhaltens ermöglicht es Ihnen, den Versand an Ihre spezifischen Anforderungen und die Leistungsfähigkeit Ihres Backends anzupassen.

**Wichtig:**

* Die genaue Implementierung und die verfügbaren Konfigurationsoptionen können je nach verwendeter OpenTelemetry-Sprach-SDK variieren.
* Die Wahl des richtigen Batching-Intervalls und der Batch-Größe hängt von verschiedenen Faktoren ab, wie z.B. dem Volumen der Telemetriedaten, der Netzwerklatenz und der Kapazität des Backends. Es ist wichtig, diese Parameter sorgfältig zu testen und zu optimieren, um eine optimale Leistung zu gewährleisten.

Here's an example of how you might represent performance data for several HTTP requests and responses using JSON, keeping in mind that OpenTelemetry primarily uses OTLP and not JSON for transmission. This example shows how span data from HTTP requests could be *represented* in JSON after being exported and transformed, perhaps for a system that doesn't support OTLP directly.

**Example JSON Structure for Multiple HTTP Requests (Inspired by OpenTelemetry Spans):**

```json
[
  {
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "spanId": "00f067aa0ba902b7",
    "parentSpanId": null,
    "name": "HTTP GET /api/users",
    "kind": "SERVER",
    "startTimeUnixNano": "1678886400000000000",
    "endTimeUnixNano": "1678886400150000000",
    "attributes": {
      "http.method": "GET",
      "http.url": "https://api.example.com/api/users",
      "http.target": "/api/users",
      "http.host": "api.example.com",
      "http.scheme": "https",
      "http.status_code": 200,
      "http.response_content_length": "1234",
      "net.peer.ip": "192.168.1.10",
      "net.peer.port": "443"
    },
    "status": {
      "code": "OK"
    }
  },
  {
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "spanId": "74755584d576b4d9",
    "parentSpanId": "00f067aa0ba902b7",
    "name": "HTTP GET /api/users/123",
    "kind": "CLIENT",
    "startTimeUnixNano": "1678886400050000000",
    "endTimeUnixNano": "1678886400100000000",
    "attributes": {
      "http.method": "GET",
      "http.url": "https://internal-api/api/users/123",
      "http.target": "/api/users/123",
      "http.host": "internal-api",
      "http.scheme": "https",
      "http.status_code": 200,
      "http.response_content_length": "256",
      "net.peer.ip": "10.0.0.5",
      "net.peer.port": "8080"
    },
    "status": {
      "code": "OK"
    }
  },
  {
    "traceId": "8a3c60f7d4dff4d6b2f9f8e7d8d7c8f7",
    "spanId": "245fa4b9655567cd",
    "parentSpanId": null,
    "name": "HTTP POST /api/orders",
    "kind": "SERVER",
    "startTimeUnixNano": "1678886401000000000",
    "endTimeUnixNano": "1678886401500000000",
    "attributes": {
      "http.method": "POST",
      "http.url": "https://api.example.com/api/orders",
      "http.target": "/api/orders",
      "http.host": "api.example.com",
      "http.scheme": "https",
      "http.status_code": 201,
      "http.request_content_length": "567",
      "net.peer.ip": "192.168.1.20",
      "net.peer.port": "443"
    },
    "status": {
      "code": "OK"
    }
  },
  {
    "traceId": "8a3c60f7d4dff4d6b2f9f8e7d8d7c8f7",
    "spanId": "195ee4b965556711",
    "parentSpanId": "245fa4b9655567cd",
    "name": "database.query",
    "kind": "CLIENT",
    "startTimeUnixNano": "1678886401100000000",
    "endTimeUnixNano": "1678886401400000000",
    "attributes": {
      "db.system": "postgresql",
      "db.statement": "INSERT INTO orders (user_id, product_id) VALUES ($1, $2)",
      "net.peer.ip": "10.0.0.10",
      "net.peer.port": "5432"
    },
    "status": {
      "code": "OK"
    }
  },
  {
    "traceId": "f4a7b8c9d0e1f23456789abcdef01234",
    "spanId": "c3d4e5f6a7b89012",
    "parentSpanId": null,
    "name": "HTTP GET /api/products/99",
    "kind": "SERVER",
    "startTimeUnixNano": "1678886402000000000",
    "endTimeUnixNano": "1678886402200000000",
    "attributes": {
      "http.method": "GET",
      "http.url": "https://api.example.com/api/products/99",
      "http.target": "/api/products/99",
      "http.host": "api.example.com",
      "http.scheme": "https",
      "http.status_code": 404,
      "http.response_content_length": "42",
      "net.peer.ip": "192.168.1.30",
      "net.peer.port": "443"
    },
    "status": {
      "code": "ERROR",
      "message": "Not Found"
    }
  }
]
```

**Explanation of the Fields:**

*   **`traceId`:** A unique identifier for the entire request trace (all related spans).
*   **`spanId`:** A unique identifier for a specific operation within the trace (a single span).
*   **`parentSpanId`:** The `spanId` of the span that caused this span to be created. `null` indicates a root span.
*   **`name`:** A human-readable name for the operation (e.g., "HTTP GET /api/users").
*   **`kind`:**  Indicates the type of span:
    *   `SERVER`: Represents the server side of an RPC or a process starting a trace.
    *   `CLIENT`: Represents the client side of an RPC.
    *   `INTERNAL`: Indicates an internal operation within an application.
    *   `PRODUCER`: Represents a producer in an asynchronous messaging scenario.
    *   `CONSUMER`: Represents a consumer in an asynchronous messaging scenario.
*   **`startTimeUnixNano`:** The start time of the span in nanoseconds since the Unix epoch (UTC).
*   **`endTimeUnixNano`:** The end time of the span in nanoseconds since the Unix epoch (UTC).
*   **`attributes`:** Key-value pairs providing more context about the operation. These follow OpenTelemetry's semantic conventions (e.g., `http.method`, `http.status_code`, `net.peer.ip`).
    *   **`http.method`:** The HTTP method (GET, POST, etc.).
    *   **`http.url`:** The full URL of the request.
    *   **`http.target`:** The path and query string of the request.
    *   **`http.host`:** The hostname from the URL.
    *   **`http.scheme`:** The URL scheme (http or https).
    *   **`http.status_code`:** The HTTP status code of the response.
    *   **`http.response_content_length`:** The size of the response body in bytes.
    *   **`http.request_content_length`:** The size of the request body in bytes.
    *   **`net.peer.ip`:** The IP address of the client or server.
    *   **`net.peer.port`:** The port number of the client or server.
    *   **`db.system`:** Type of the database system (e.g. postgresql, mysql)
    *   **`db.statement`:** SQL query for database operations.
*   **`status`:** Information about the outcome of the operation.
    *   **`code`:**  `OK`, `ERROR`, or `UNSET`.
    *   **`message`:** An error message (if applicable).

**Important Considerations:**

*   **OTLP is Preferred:** This is a JSON representation *for illustrative purposes*. OpenTelemetry uses OTLP, which is more efficient.
*   **Semantic Conventions:**  The `attributes` use OpenTelemetry's semantic conventions. You can find a comprehensive list of these conventions in the OpenTelemetry specification. These conventions provide a common vocabulary for describing various types of operations.
*   **Custom Attributes:** You can add your own custom attributes to spans to capture application-specific data.
*   **Tools for Transformation:** If you need to transform OTLP data to JSON, you can use tools like the OpenTelemetry Collector, which can export data in various formats, or you can write custom code to perform the transformation after receiving the data from an OTLP exporter.

This comprehensive example helps you understand how you can represent OpenTelemetry performance data in JSON format, even though it's not the standard way OpenTelemetry transmits data. Remember to use OTLP if you can. Use this JSON representation for compatibility with systems that need it.

## Dokumentation: OpenTelemetry Monitoring für Resource Server in Zero-Trust-Architektur

### 1. Einführung

Diese Dokumentation beschreibt, wie OpenTelemetry verwendet werden kann, um wichtige Betriebsdaten eines Resource Servers zu erfassen, der durch eine Zero-Trust-Architektur mit Policy Decision Point (PDP) und Policy Enforcement Point (PEP) geschützt ist.  Der Fokus liegt auf der Erfassung von Performance- und Lastmetriken sowie der Erkennung und Erfassung von Fehlermeldungen. Die Daten werden über OpenTelemetry erfasst, verarbeitet und an eine zentrale Stelle zur Analyse und Visualisierung weitergeleitet.

### 2. Architekturübersicht

```
[Client] --> [PEP] --> [Resource Server]
             ^
             |
             [OpenTelemetry Agent (PEP)] --> [ZETA Guard OpenTelemetry Collector] <--> [Monitoring des Anbieters]
                                             |
                                             v 
                                             [BDE OpenTelemetry Collector]
                                             |
                                             v 
                                             [Backend (z.B. DB, Grafana, Prometheus, Jaeger)]
```

* **Client:**  Der Benutzer oder die Anwendung, die auf den Resource Server zugreifen möchte.
* **PEP (Policy Enforcement Point):**  Der PEP ist der vorgeschaltete Gateway zum Resource Server. Er setzt die vom PDP definierten Zugriffsrichtlinien durch. In dieser Architektur ist der PEP der ideale Punkt, um OpenTelemetry zu integrieren, da er jeden Request und Response passieren sieht.
* **Resource Server:** Der eigentliche Server, der die geschützten Ressourcen bereitstellt.
* **OpenTelemetry Agent (PEP):**  Ein OpenTelemetry Agent wird am PEP installiert. Dieser Agent instrumentiert den PEP (z.B. durch Auto-Instrumentation für HTTP-Server-Bibliotheken) oder wird manuell instrumentiert, um Telemetriedaten zu erfassen.
* **ZETA Guard OpenTelemetry Collector:**  Der Collector empfängt die von den Agents gesammelten Daten, verarbeitet sie (z.B. Batching, Sampling, Anreicherung) und exportiert sie an den BDE OpenTelemetry Collector.
* **Backend (z.B. DB, Grafana, Prometheus):**  Ein Speichersystem und Visualisierungswerkzeug für die Telemetriedaten. Prometheus ist ideal für Metriken.

### 3. Datenerfassung durch OpenTelemetry am PEP

OpenTelemetry erfasst Rohdaten zu Requests und Responses auf folgende Weise:

* **Auto-Instrumentation (Empfohlen):**  OpenTelemetry bietet Auto-Instrumentation-Bibliotheken für gängige Programmiersprachen und Frameworks (z.B. für Java, Python, Node.js, Go). Diese Bibliotheken instrumentieren automatisch HTTP-Server-Bibliotheken, die im PEP verwendet werden. Dadurch werden Spans für eingehende HTTP-Requests und ausgehende HTTP-Responses erzeugt, ohne Code-Änderungen im PEP selbst.
* **Manuelle Instrumentation (Optional):**  Falls Auto-Instrumentation nicht ausreichend ist oder spezifische Anpassungen benötigt werden, kann der PEP-Code manuell mit OpenTelemetry SDKs instrumentiert werden. Dies erfordert Code-Änderungen, bietet aber maximale Flexibilität.

**Erfasste Rohdaten (pro Request/Response Span):**

* **Request:**
    * **Startzeitpunkt:**  Zeitpunkt, zu dem der Request am PEP eintrifft.
    * **HTTP-Methode:**  GET, POST, PUT, DELETE, etc.
    * **Pfad (Path):**  Der angefragte Pfad des Resource Servers (z.B. `/api/produkte`).
    * **Request-Header:**  Alle Request-Header, die der Client gesendet hat (werden für die Metrikberechnung **nicht direkt** verwendet, können aber für detailliertere Analysen erfasst werden).
* **Response:**
    * **Endzeitpunkt:**  Zeitpunkt, zu dem die Response vom Resource Server am PEP eintrifft (und an den Client zurückgesendet wird).
    * **HTTP-Statuscode:**  200, 404, 500, etc.
    * **Response-Header:**  Alle Response-Header, die der Resource Server gesendet hat, inklusive des **`ZETA-Cause`** Headers im Fehlerfall.

### 4. Berechnung von Performance und Last Metriken

OpenTelemetry nutzt die erfassten Rohdaten, um automatisch Metriken zu berechnen:

* **Performance (Latenz pro Endpunkt):**
    * **Berechnung:**  Die Latenz für einen Request wird als die Differenz zwischen dem `Endzeitpunkt` des Responses und dem `Startzeitpunkt` des Requests berechnet.  Dies repräsentiert die **End-to-End-Latenz** aus Sicht des PEP (und somit annähernd aus Client-Sicht).
    * **Metrik-Typ:**  **Histogramm** oder **Summary**. Diese Metriktypen sind ideal, um die Verteilung der Latenzzeiten über verschiedene Requests hinweg darzustellen (z.B. Durchschnitt, Perzentile).
    * **Attribute:**
        * `http.method`: HTTP-Methode des Requests (z.B. `GET`, `POST`).
        * `http.route`: Der **geroutete Pfad** des Endpunkts (wichtig, um ähnliche Pfade zu gruppieren, z.B. `/api/produkte/{produktId}` wird zu `/api/produkte/{produktId}`).  OpenTelemetry Instrumentierungen extrahieren oft automatisch die Route.
        * `http.status_code`: HTTP-Statuscode des Responses.

* **Last (Anzahl der Requests pro Zeiteinheit):**
    * **Berechnung:**  Die Last wird als die **Anzahl der Requests** über einen bestimmten Zeitraum (z.B. pro Minute, pro 5 Minuten) gezählt.
    * **Metrik-Typ:**  **Counter**. Ein Counter wird bei jedem eingehenden Request inkrementiert.
    * **Attribute:**
        * `http.method`: HTTP-Methode des Requests.
        * `http.route`: Der geroutete Pfad des Endpunkts.
        * `http.status_code`: HTTP-Statuscode des Responses (um z.B. erfolgreiche und fehlerhafte Requests separat zu zählen).

### 5. Erfassung von Fehlermeldungen (ZETA-Cause Header)

Der `ZETA-Cause` Header im Response enthält Fehlerinformationen. OpenTelemetry kann diese Informationen extrahieren und für Metriken und ggf. Logs nutzen:

* **Extraktion des Headers:**  Über OpenTelemetry Processors (siehe Konfiguration) oder in manueller Instrumentation kann der `ZETA-Cause` Header aus dem Response extrahiert werden.
* **Fehlerzählung:**
    * **Metrik-Typ:**  **Counter**. Ein separater Counter für Fehlerfälle.
    * **Bedingung:**  Inkrementiere den Counter, wenn der `ZETA-Cause` Header im Response vorhanden ist **oder** der HTTP-Statuscode im Fehlerbereich liegt (z.B. 4xx oder 5xx).
    * **Attribute:**
        * `zeta.cause.code`:  Fehlernummer aus dem `ZETA-Cause` Header.
        * `zeta.cause.description`: Kurzbeschreibung aus dem `ZETA-Cause` Header.
        * `http.status_code`:  HTTP-Statuscode des Responses.
        * `http.route`: Der geroutete Pfad des Endpunkts.

* **Logs (Optional):**  Für detailliertere Fehleranalyse können Fehlerereignisse auch als Logs erfasst werden, inklusive der extrahierten `ZETA-Cause` Informationen und des gesamten Response-Headers. Dies ist hilfreich für Debugging, sollte aber sparsam eingesetzt werden, um die Menge an Logdaten zu begrenzen.

### 6. Zusätzliche Metriken

Zusätzlich zu den Kernmetriken (Performance, Last, Fehler) könnten folgende Metriken nützlich sein:

* **HTTP Status Code Verteilung:**
    * **Metrik-Typ:**  Counter.  Separate Counter für jeden wichtigen HTTP Statuscode-Bereich (z.B. `http.status_code: 2xx`, `http.status_code: 4xx`, `http.status_code: 5xx`).
    * **Zweck:**  Überblick über die Art der Responses (Erfolg, Client-Fehler, Server-Fehler).
* **Request-Größe und Response-Größe:**
    * **Metrik-Typ:** Histogramm oder Gauge.
    * **Zweck:**  Analyse des Datenvolumens, Bandbreitenverbrauch, potentielle Engpässe.
* **Anzahl abgelehnter Requests durch PDP/PEP:**
    * **Metrik-Typ:** Counter.
    * **Bedingung:**  Inkrementiere den Counter, wenn der PEP einen Request aufgrund einer Policy-Entscheidung des PDP ablehnt (z.B. HTTP Statuscode 403).
    * **Zweck:**  Überwachung der Effektivität der Zero-Trust-Richtlinien und potenzieller Fehlkonfigurationen.
* **PEP-Performance (optional):**
    * **Metrik-Typ:** Histogramm.
    * **Messung:**  Latenz der Policy-Entscheidung im PEP selbst (Zeit zwischen Request-Empfang und Weiterleitung an den Resource Server).
    * **Zweck:**  Überwachung der Performance des PEP selbst und Identifizierung potenzieller Engpässe im PEP oder PDP.

### 7. Beispiel-Daten und Konfiguration

#### 7.1 Beispiel-Daten (Prometheus Exposition Format)

```
# HELP http_server_duration_seconds Histogram of HTTP server request durations.
# TYPE http_server_duration_seconds histogram
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.005"} 10
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.01"} 50
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.025"} 120
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.05"} 250
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.1"} 400
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.25"} 480
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="0.5"} 495
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="1.0"} 500
http_server_duration_seconds_bucket{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200",le="+Inf"} 500
http_server_duration_seconds_sum{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200"} 12.5
http_server_duration_seconds_count{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200"} 500

# HELP http_server_requests_total Total number of HTTP server requests.
# TYPE http_server_requests_total counter
http_server_requests_total{http_method="GET",http_route="/api/produkte/{produktId}",http_status_code="200"} 500
http_server_requests_total{http_method="POST",http_route="/api/bestellungen",http_status_code="201"} 150
http_server_requests_total{http_method="GET",http_route="/api/produkte",http_status_code="500"} 10
http_server_requests_total{http_method="GET",http_route="/api/produkte",http_status_code="404"} 5

# HELP zeta_cause_errors_total Total number of errors reported via ZETA-Cause header.
# TYPE zeta_cause_errors_total counter
zeta_cause_errors_total{zeta_cause_code="ERR-1001",zeta_cause_description="Datenbankfehler",http_status_code="500",http_route="/api/produkte"} 3
zeta_cause_errors_total{zeta_cause_code="ERR-2005",zeta_cause_description="Ungültige Eingabe",http_status_code="400",http_route="/api/bestellungen"} 2

# HELP http_server_status_codes_total Total count of HTTP status codes.
# TYPE http_server_status_codes_total counter
http_server_status_codes_total{http_status_code="2xx"} 650
http_server_status_codes_total{http_status_code="4xx"} 7
http_server_status_codes_total{http_status_code="5xx"} 10
```

#### 7.2 Beispiel-Daten im OTLP Format (Strukturierte Darstellung)

**Wichtiger Hinweis:** OTLP ist ein binäres Protokoll (meist Protobuf oder gRPC).  Die hier gezeigten Beispiele sind **keine direkte binäre Repräsentation**. Stattdessen handelt es sich um eine **strukturierte, textuelle Darstellung**, die die logische Struktur von OTLP Datenpunkten und Metriken verdeutlicht.  In der Praxis würden OTLP Daten als binäre Protobuf-Nachrichten über das Netzwerk gesendet.

Wir konzentrieren uns auf die gleichen Metrik-Beispiele wie im Prometheus Format (Performance, Last, ZETA-Cause Fehler).

**1. HTTP Server Request Duration (Histogramm)**

* **Metrik-Name:** `http.server.duration` (Konventionell in OTel für HTTP Server Duration)
* **Daten-Typ:** Histogram
* **Einheit:** Sekunden (`s`)

```
Metric:
  name: "http.server.duration"
  unit: "s"
  data: Histogram
    data_points:
      - attributes:
          - key: "http.method"
            value: "GET"
          - key: "http.route"
            value: "/api/produkte/{produktId}"
          - key: "http.status_code"
            value: "200"
        start_time_unix_nano: <Timestamp 1>  # Startzeit des Messintervalls
        time_unix_nano: <Timestamp 2>     # Endzeit des Messintervalls
        count: 500                        # Anzahl der Messungen im Intervall
        sum: 12.5                         # Summe aller Messwerte
        bucket_counts: [10, 40, 70, 130, 150, 80, 15, 5] # Anzahl in jedem Bucket (bis zum jeweiligen Upper Bound)
        explicit_bounds: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0] # Bucket Grenzen (Upper Bounds)

      # ... weitere Datenpunkte für andere Methoden, Routen, Statuscodes ...

```

**Erläuterung Histogramm:**

* `name`: Der Name der Metrik.
* `unit`: Die Einheit der Metrik (Sekunden).
* `data: Histogram`:  Kennzeichnet den Metrik-Typ als Histogramm.
* `data_points`: Eine Liste von einzelnen Datenpunkten.
* `attributes`:  Die Dimensionen/Labels, die diesen Datenpunkt identifizieren (Methode, Route, Statuscode).
* `start_time_unix_nano`, `time_unix_nano`:  Zeitintervalle für die Aggregation.
* `count`, `sum`:  Zusammenfassende Werte für das Histogramm.
* `bucket_counts`, `explicit_bounds`: Definiert die Histogramm-Buckets und deren Zählwerte.

**2. HTTP Server Requests Total (Counter)**

* **Metrik-Name:** `http.server.requests_count` (oder `http.server.request.count` - Konventionen können leicht variieren)
* **Daten-Typ:** Summe (Counter ist ein Spezialfall einer Summe mit Monotonicity = INCREMENTING)
* **Einheit:** `{requests}` (Anzahl Anfragen, dimensionslos)

```
Metric:
  name: "http.server.requests_count"
  unit: "{requests}"
  data: Sum
    aggregation_temporality: CUMULATIVE # Oder DELTA, je nach Konfiguration
    is_monotonic: true # Counter sind immer monoton steigend
    data_points:
      - attributes:
          - key: "http.method"
            value: "GET"
          - key: "http.route"
            value: "/api/produkte/{produktId}"
          - key: "http.status_code"
            value: "200"
        start_time_unix_nano: <Timestamp 3>
        time_unix_nano: <Timestamp 4>
        value: 500 # Aktueller Zählerstand

      - attributes:
          - key: "http.method"
            value: "POST"
          - key: "http.route"
            value: "/api/bestellungen"
          - key: "http.status_code"
            value: "201"
        start_time_unix_nano: <Timestamp 5>
        time_unix_nano: <Timestamp 6>
        value: 150

      # ... weitere Datenpunkte ...
```

**Erläuterung Counter:**

* `name`: Metrik-Name.
* `unit`: Einheit (Anzahl Requests).
* `data: Sum`: Kennzeichnet Summen-Metrik (Counter).
* `aggregation_temporality`:  `CUMULATIVE` (Zählerstand seit Start) oder `DELTA` (Änderung im letzten Intervall).  `CUMULATIVE` ist typischer für Counter.
* `is_monotonic: true`:  Bestätigt, dass es sich um einen monoton steigenden Zähler handelt.
* `data_points`: Datenpunkte.
* `attributes`: Dimensionen.
* `value`: Der aktuelle Zählerwert.

**3. ZETA-Cause Fehler Counter**

* **Metrik-Name:** `zeta.cause.errors_total` (oder prägnanter z.B. `zeta.errors.count`)
* **Daten-Typ:** Summe (Counter)
* **Einheit:** `{errors}`

```
Metric:
  name: "zeta.cause.errors_total"
  unit: "{errors}"
  data: Sum
    aggregation_temporality: CUMULATIVE
    is_monotonic: true
    data_points:
      - attributes:
          - key: "zeta.cause.code"
            value: "ERR-1001"
          - key: "zeta.cause.description"
            value: "Datenbankfehler"
          - key: "http.status_code"
            value: "500"
          - key: "http.route"
            value: "/api/produkte"
        start_time_unix_nano: <Timestamp 7>
        time_unix_nano: <Timestamp 8>
        value: 3

      - attributes:
          - key: "zeta.cause.code"
            value: "ERR-2005"
          - key: "zeta.cause.description"
            value: "Ungültige Eingabe"
          - key: "http.status_code"
            value: "400"
          - key: "http.route"
            value: "/api/bestellungen"
        start_time_unix_nano: <Timestamp 9>
        time_unix_nano: <Timestamp 10>
        value: 2

      # ... weitere Fehler ...
```

**Erläuterung ZETA-Cause Counter:**

* Analog zum Request Counter, aber mit zusätzlichen Attributen für `zeta.cause.code` und `zeta.cause.description`, um die Fehlerursachen zu differenzieren.

**Wichtige Punkte zu OTLP:**

* **Binär:**  Wie bereits betont, ist OTLP binär. Diese strukturierte Textform dient nur zur Veranschaulichung.
* **Protokoll-Flexibilität:** OTLP kann über gRPC oder HTTP/Protobuf übertragen werden.
* **Erweiterbarkeit:** OTLP ist darauf ausgelegt, erweiterbar zu sein. Sie können eigene Attribute und Metriken hinzufügen.
* **Standardisierung:** OTLP ist der empfohlene Standard für Telemetriedaten in OpenTelemetry und wird von vielen Backend-Systemen unterstützt.

**Verwendung mit Collector und Backend:**

Der OpenTelemetry Collector würde diese OTLP Daten von den Agenten empfangen, verarbeiten und dann in das gewünschte Backend-Format (z.B. Prometheus, Jaeger, Zipkin, Datenbanken) exportieren.  Wenn Sie Prometheus als Backend verwenden, würde der Collector die OTLP Metriken in das Prometheus Exposition Format umwandeln, bevor er sie für Prometheus zum Scrapen bereitstellt (oder per Push, je nach Konfiguration).

Diese Beispiele sollten Ihnen ein besseres Verständnis dafür geben, wie Metriken in OTLP strukturiert sind und wie sie Ihre Performance-, Last- und Fehlerdaten repräsentieren könnten.

#### 7.3 Beispiel-Konfiguration (OpenTelemetry Collector - YAML)

Dieses Beispiel zeigt eine Collector-Konfiguration, die:

1. **OTLP-Protokoll** als Eingang für Daten vom Agenten verwendet.
2. Einen **Batch-Prozessor** verwendet, um Daten effizient zu bündeln.
3. Einen **Attribute-Prozessor** verwendet, um den `ZETA-Cause` Header zu extrahieren und als Attribute hinzuzufügen.
4. Daten an einen **Prometheus Exporter** und optional an einen **Logging Exporter** weiterleitet.

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:
  attributes/extract_zeta_cause:
    actions:
      - action: insert
        key: zeta.cause.code
        from_attribute: http.response.header.zeta-cause
        pattern: '^(.*?):'  # Regex to extract code before colon
      - action: insert
        key: zeta.cause.description
        from_attribute: http.response.header.zeta-cause
        pattern: '^.*?:(.*)$' # Regex to extract description after colon

exporters:
  prometheus:
    endpoint: ":8889" # Prometheus Endpoint für Scrapping
  logging: # Optional für Debugging
    loglevel: debug

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch, attributes/extract_zeta_cause] # Wichtig: Attribute-Prozessor vor dem Export!
      exporters: [prometheus, logging]
```

#### 7.4 Beispiel-Konfiguration (OpenTelemetry Agent - Code, Python mit Flask)

Dieses Beispiel zeigt, wie Auto-Instrumentation in Python mit Flask verwendet werden kann und ein OTLP Exporter konfiguriert wird.  **Hinweis:** Der PEP müsste in Python und Flask implementiert sein, um dieses Beispiel direkt zu verwenden. Das Prinzip ist aber in anderen Sprachen und Frameworks ähnlich.

```python
from flask import Flask
import requests
import os
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metrics_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

app = Flask(__name__)

# OpenTelemetry Resource (optional, aber empfolen)
resource = Resource.create({
    "service.name": "pep-service",
    "service.version": "1.0.0",
    "environment": "production" # oder development, staging, etc.
})

# Tracer Provider
tracer_provider = TracerProvider(resource=resource)
span_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True) # Collector Adresse
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)

# Meter Provider
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True)) # Collector Adresse
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Instrumentation
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument() # Instrumentiert outgoing Requests, falls der PEP selbst Requests macht

@app.route("/protected-resource")
def protected_resource():
    # ... PEP Logik (Policy Enforcement, PDP Anfrage etc.) ...

    # Beispiel: Weiterleitung zum Resource Server
    resource_server_url = "http://resource-server:8080/api/daten"
    response = requests.get(resource_server_url)

    # ... Response Verarbeitung ...

    return response.text, response.status_code, response.headers.items()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
```

### 8. Zusammenfassung und Empfehlungen

OpenTelemetry bietet eine leistungsstarke und flexible Lösung, um Performance, Last und Fehler Ihres Resource Servers in einer Zero-Trust-Architektur zu überwachen.

**Wichtige Empfehlungen:**

* **Auto-Instrumentation nutzen:** Wo immer möglich, nutzen Sie Auto-Instrumentation, um den Aufwand zu minimieren und konsistente Daten zu erhalten.
* **Attribute nutzen:** Verwenden Sie Attribute, um Metriken mit Kontextinformationen anzureichern (HTTP-Methode, Route, Statuscode, Fehlercodes).
* **Collector konfigurieren:**  Nutzen Sie den OpenTelemetry Collector, um Daten zu verarbeiten, anzureichern und an verschiedene Backends zu exportieren.
* **Backend wählen:** Wählen Sie ein geeignetes Backend für Ihre Anforderungen (Prometheus für Metriken, Jaeger/Tempo für Traces, etc.).
* **Dashboards erstellen:**  Visualisieren Sie die erfassten Metriken in Dashboards (z.B. mit Grafana), um einen Echtzeit-Überblick über den Zustand und die Performance des Resource Servers zu erhalten.
* **Alerting einrichten:**  Konfigurieren Sie Alerting-Regeln basierend auf den Metriken, um bei Problemen (z.B. hohe Latenz, hohe Fehlerrate) frühzeitig benachrichtigt zu werden.

Diese Dokumentation bietet Ihnen einen umfassenden Leitfaden zur Implementierung von OpenTelemetry Monitoring in Ihrer Zero-Trust-Umgebung. Passen Sie die Konfiguration und die Metriken an Ihre spezifischen Anforderungen an, um das bestmögliche Monitoring zu erreichen.

## OpenTelemetry Collector Deployment

The OpenTelemetry Collector is a crucial component that acts as a vendor-agnostic intermediary for receiving, processing, and exporting telemetry data. You'll deploy it within your Kubernetes cluster.

*   **Deployment Modes:**
    *   **Agent:** Deploy the Collector as a DaemonSet to run an instance on each node. This is suitable for collecting node-level metrics and logs and for forwarding telemetry data from applications running on the same node.
    *   **Sidecar:** Deploy a Collector instance alongside each application pod. Useful for application-specific processing or when strict network isolation is required.
    *   **Gateway:** Deploy the Collector as a Deployment (with multiple replicas for high availability). This is the most common mode and acts as a central point for receiving data from agents, sidecars, or directly from applications. It can also perform more complex processing and filtering before sending data to backends.

*   **Configuration (config.yaml):**
    *   **Receivers:** Define how the Collector will receive data. Common receivers include:
        *   `otlp`: Receives data in the OpenTelemetry Protocol format (gRPC or HTTP).
        *   `jaeger`: Receives data in Jaeger format.
        *   `zipkin`: Receives data in Zipkin format.
        *   `hostmetrics`: (For agents) Scrapes host-level metrics.
        *   `kubeletstats`: (For agents) Scrapes container metrics from the Kubelet.
        *   `kubernetes_cluster`: Receives cluster-level metrics.
    *   **Processors:** (Optional) Define how to process the data. Common processors include:
        *   `batch`: Batches data before sending it to exporters, improving performance.
        *   `memory_limiter`: Prevents the Collector from consuming too much memory.
        *   `attributes`: Adds, modifies, or deletes attributes.
        *   `resource`: Adds, modifies, or deletes resource attributes.
        *   `filter`: Filters spans, metrics or logs based on certain criteria.
    *   **Exporters:** Define where to send the processed data. Common exporters include:
        *   `otlp`: Sends data to another OTLP endpoint (e.g., another Collector, an observability backend).
        *   `jaeger`: Sends data to a Jaeger backend.
        *   `zipkin`: Sends data to a Zipkin backend.
        *   `prometheus`: Exposes metrics in Prometheus format.
        *   `logging`: Logs the data to the console (useful for debugging).
    *   **Service:** Defines the pipelines that connect receivers, processors, and exporters.

**Example `config.yaml` (Gateway Deployment):**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:
    timeout: 10s
  memory_limiter:
    check_interval: 1s
    limit_mib: 2048
  resource:
    attributes:
    - key: environment
      value: production
      action: upsert

exporters:
  otlp: # Example: sending to another OTLP endpoint like Honeycomb, Lightstep
    endpoint: "api.honeycomb.io:443"
    headers:
      "x-honeycomb-team": "YOUR_HONEYCOMB_API_KEY"
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, memory_limiter]
      exporters: [otlp, logging]
    metrics:
      receivers: [otlp]
      processors: [batch, memory_limiter, resource]
      exporters: [otlp]
```

*   **Deployment (YAML):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opentelemetry-collector
  namespace: monitoring # example namespace
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opentelemetry-collector
  template:
    metadata:
      labels:
        app: opentelemetry-collector
    spec:
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:latest # Or a specific version
          command:
            - "/otelcol-contrib"
            - "--config=/conf/config.yaml"
          args:
            - --log-level=DEBUG
          ports:
            - containerPort: 4317 # OTLP gRPC
            - containerPort: 4318 # OTLP HTTP
            - containerPort: 8888 # Metrics
            - containerPort: 55679 # zPages (for debugging)
          volumeMounts:
            - name: otel-collector-config-vol
              mountPath: /conf
      volumes:
        - name: otel-collector-config-vol
          configMap:
            name: otel-collector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: monitoring
data:
  config.yaml: |
    # --- Paste your config.yaml content here ---
---
apiVersion: v1
kind: Service
metadata:
  name: opentelemetry-collector
  namespace: monitoring
spec:
  selector:
    app: opentelemetry-collector
  ports:
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: otlp-http
      port: 4318
      targetPort: 4318
    - name: metrics
      port: 8888
      targetPort: 8888
```

## Backend Systems

*   **Choose Backends:** Select the observability backend(s) where you want to store and analyze your telemetry data. Popular options include:
    *   **Open Source:** Jaeger, Zipkin (for traces), Prometheus, Grafana (for metrics and visualizations), Elasticsearch, Fluentd, Kibana (for logs).
    *   **Commercial:** Honeycomb, Lightstep, Datadog, New Relic, Dynatrace, AWS X-Ray.
*   **Configure Exporters:** Configure the appropriate exporters in your OpenTelemetry Collector's `config.yaml` to send data to your chosen backends.

**4. Deployment and Verification**

1. **Deploy the Collector:** Apply the Collector's deployment YAML to your Kubernetes cluster using `kubectl apply -f collector.yaml`.
2. **Deploy Applications:** Deploy your instrumented applications to Kubernetes.
3. **Verify:**
    *   Check the Collector logs to ensure it's receiving data and not reporting errors. Use `kubectl logs -f deployment/opentelemetry-collector -n monitoring`.
    *   Use the observability backend's UI to view your traces, metrics, and logs. You should be able to see data flowing in from your applications.

**5. Advanced Considerations**

*   **Auto-Instrumentation with Operator:** The OpenTelemetry Operator for Kubernetes can simplify instrumentation by automatically injecting the necessary SDKs and configurations into your application pods.
*   **Sampling:** To reduce the volume of data sent to backends, especially for high-traffic services, configure sampling in your application's tracer or in the Collector's processors.
*   **Security:**
    *   Use TLS for communication between your applications, the Collector, and backends.
    *   Secure the Collector's endpoints (e.g., using network policies).
*   **Resource Management:** Monitor the Collector's resource usage (CPU, memory) and adjust resource limits and requests as needed.
*   **High Availability:** Deploy the Collector in Gateway mode with multiple replicas for high availability and fault tolerance.
*   **Logs:** While OpenTelemetry is primarily focused on traces and metrics, you can also use the Collector to receive and process logs. You can use a sidecar container running Fluent Bit or Fluentd to forward logs to the OpenTelemetry Collector.
*   **Custom Processors:** For more advanced use cases, write custom processors for the Collector to implement specific filtering, transformation, or enrichment logic.

By following these steps, you can successfully deploy and use OpenTelemetry in your Kubernetes environment to gain deep insights into the performance and behavior of your microservices. Remember to tailor the configuration to your specific needs and choose the right backends for your analysis requirements. Using OpenTelemetry will significantly improve the observability of your applications and help you troubleshoot issues more effectively.
