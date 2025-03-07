# Open Telemetry

## Inhaltsverzeichnis

- [Open Telemetry](#open-telemetry)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [1. Einführung](#1-einführung)
  - [2. OpenTelemetry Monitoring für Resource Server in Zero-Trust-Architektur](#2-opentelemetry-monitoring-für-resource-server-in-zero-trust-architektur)
    - [2.1 Architekturübersicht](#21-architekturübersicht)
    - [2.2 Datenerfassung durch OpenTelemetry am PEP](#22-datenerfassung-durch-opentelemetry-am-pep)
    - [2.3 Berechnung von Performance und Last Metriken](#23-berechnung-von-performance-und-last-metriken)
    - [2.4 Erfassung von Fehlermeldungen (ZETA-Cause Header)](#24-erfassung-von-fehlermeldungen-zeta-cause-header)
    - [2.5 Zusätzliche Metriken](#25-zusätzliche-metriken)
    - [2.6 Beispiel-Daten und Konfiguration](#26-beispiel-daten-und-konfiguration)
      - [2.6.1 Beispiel-Daten (Prometheus Exposition Format)](#261-beispiel-daten-prometheus-exposition-format)
      - [2.6.2 Beispiel-Daten im OTLP Format (Strukturierte Darstellung)](#262-beispiel-daten-im-otlp-format-strukturierte-darstellung)
      - [2.6.3 Beispiel-Konfiguration (OpenTelemetry Collector - YAML)](#263-beispiel-konfiguration-opentelemetry-collector---yaml)
      - [2.6.4 Beispiel-Konfiguration (OpenTelemetry Agent - Code, Python mit Flask)](#264-beispiel-konfiguration-opentelemetry-agent---code-python-mit-flask)
  - [3. Aggregation von Metriken](#3-aggregation-von-metriken)
    - [3.1 Beispiel eines HTTP-Requests:](#31-beispiel-eines-http-requests)
    - [3.2 OpenTelemetry Header im weitergeleiteten Request](#32-opentelemetry-header-im-weitergeleiteten-request)
    - [3.3 Kann der Resource Server eigene Daten an den OpenTelemetry Collector senden?](#33-kann-der-resource-server-eigene-daten-an-den-opentelemetry-collector-senden)
    - [3.4 Wie erfolgt die Verknüpfung?](#34-wie-erfolgt-die-verknüpfung)
  - [4. Empfehlungen](#4-empfehlungen)
  - [5. Anhang, OpenTelemetry Collector Deployment](#5-anhang-opentelemetry-collector-deployment)
  - [6. Traces und Metriken in OpenTelemetry](#6-traces-und-metriken-in-opentelemetry)
  - [7. OpenTelemetry Collector Konfiguration Abschnitt für Abschnitt](#7-opentelemetry-collector-konfiguration-abschnitt-für-abschnitt)
  - [8. Referenzen](#8-referenzen)


## 1. Einführung

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

**Batching (Zusammenfassung):**

* OpenTelemetry SDKs bieten in der Regel **Batch Processors** (z.B. `BatchSpanProcessor` für Traces, `BatchLogRecordProcessor` für Logs).
* Diese Processors sammeln Telemetriedaten (Spans, Log Records, etc.) im Speicher, anstatt sie sofort zu versenden.
* Sie konfigurieren den Batch Processor mit Parametern wie:
    * **`max_queue_size`:** Die maximale Anzahl von Telemetriedaten, die im Speicher gehalten werden können.
    * **`scheduled_delay_millis`:** Das Intervall (in Millisekunden), nach dem die gesammelten Daten versendet werden (z.B. 300000 für 5 Minuten).
    * **`export_timeout_millis`:** Die maximale Zeit, die für den Export eines Batches gewartet wird.
    * **`max_export_batch_size`:** Die maximale Anzahl von Telemetriedaten, die in einem einzelnen Exportvorgang gesendet werden. Wenn der Batch größer ist, wird er in mehrere Exporte aufgeteilt.

**Scheduling (Zeitgesteuerter Versand):**

* Der Batch Processor verwendet einen internen Timer, um den Versand der gesammelten Daten in regelmäßigen Abständen auszulösen.
* Basierend auf dem konfigurierten `scheduled_delay_millis` (z.B. 5 Minuten) wird der Batch Processor die Daten an den Exporter weiterleiten.

**Exporter (Versand):**

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

## 2. OpenTelemetry Monitoring für Resource Server in Zero-Trust-Architektur

Diese Dokumentation beschreibt, wie OpenTelemetry verwendet werden kann, um wichtige Betriebsdaten eines Resource Servers zu erfassen, der durch eine Zero-Trust-Architektur mit Policy Decision Point (PDP) und Policy Enforcement Point (PEP) geschützt ist.  Der Fokus liegt auf der Erfassung von Performance- und Lastmetriken sowie der Erkennung und Erfassung von Fehlermeldungen. Die Daten werden über OpenTelemetry erfasst, verarbeitet und an eine zentrale Stelle zur Analyse und Visualisierung weitergeleitet.

### 2.1 Architekturübersicht

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

### 2.2 Datenerfassung durch OpenTelemetry am PEP

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

### 2.3 Berechnung von Performance und Last Metriken

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

### 2.4 Erfassung von Fehlermeldungen (ZETA-Cause Header)

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

### 2.5 Zusätzliche Metriken

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

### 2.6 Beispiel-Daten und Konfiguration

#### 2.6.1 Beispiel-Daten (Prometheus Exposition Format)

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

#### 2.6.2 Beispiel-Daten im OTLP Format (Strukturierte Darstellung)

**Wichtiger Hinweis:** OTLP ist ein binäres Protokoll (meist Protobuf oder gRPC).  Die hier gezeigten Beispiele sind **keine direkte binäre Repräsentation**. Stattdessen handelt es sich um eine **strukturierte, textuelle Darstellung**, die die logische Struktur von OTLP Datenpunkten und Metriken verdeutlicht.  In der Praxis würden OTLP Daten als binäre Protobuf-Nachrichten über das Netzwerk gesendet.

Wir konzentrieren uns auf die gleichen Metrik-Beispiele wie im Prometheus Format (Performance, Last, ZETA-Cause Fehler).

**HTTP Server Request Duration (Histogramm)**

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

**HTTP Server Requests Total (Counter)**

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

**ZETA-Cause Fehler Counter**

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

#### 2.6.3 Beispiel-Konfiguration (OpenTelemetry Collector - YAML)

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

#### 2.6.4 Beispiel-Konfiguration (OpenTelemetry Agent - Code, Python mit Flask)

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

## 3. Aggregation von Metriken

Hier sind Beispiel-OpenTelemetry-Daten, die der OpenTelemetry Agent des HTTP-Proxies an den OpenTelemetry Collector sendet:

### 3.1 Beispiel eines HTTP-Requests:
```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "zero-trust-pep"}},
          {"key": "host.name", "value": {"stringValue": "pep.example.com"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {
            "name": "auto-instrumentation"
          },
          "spans": [
            {
              "traceId": "abc1234567890def",
              "spanId": "1234567890abcd",
              "parentSpanId": null,
              "name": "HTTP GET /protected-resource",
              "kind": 2, 
              "startTimeUnixNano": "1707575200000000000",
              "endTimeUnixNano": "1707575201000000000",
              "attributes": [
                {"key": "http.method", "value": {"stringValue": "GET"}},
                {"key": "http.url", "value": {"stringValue": "https://resource-server.example.com/protected-resource"}},
                {"key": "http.status_code", "value": {"intValue": 200}},
                {"key": "http.user_agent", "value": {"stringValue": "Mozilla/5.0"}},
                {"key": "zero_trust.authenticated", "value": {"boolValue": true}},
                {"key": "zero_trust.token_jti", "value": {"stringValue": "token-xyz-123"}},
                {"key": "zero_trust.client_id", "value": {"stringValue": "client-abc"}}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 3.2 OpenTelemetry Header im weitergeleiteten Request
Ja, der HTTP Proxy kann OpenTelemetry Header im Request an den Resource Server weiterleiten, insbesondere den `traceparent`-Header, der eine bestehende Trace-ID weitergibt. Beispiel für HTTP-Header des weitergeleiteten Requests:

```
GET /protected-resource HTTP/1.1
Host: resource-server.example.com
Authorization: Bearer eyJhbGciOiJI...
traceparent: 00-abc1234567890def-1234567890abcd-01
```

### 3.3 Kann der Resource Server eigene Daten an den OpenTelemetry Collector senden?
Der Resource Server kann ebenfalls OpenTelemetry-Daten an den OpenTelemetry Collector senden und diese mit den Daten des HTTP-Proxies verknüpfen, indem er die `traceId` aus dem `traceparent`-Header übernimmt.

**Beispiel für die Daten des Resource Servers:**
```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "resource-server"}},
          {"key": "host.name", "value": {"stringValue": "resource-server.example.com"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {
            "name": "auto-instrumentation"
          },
          "spans": [
            {
              "traceId": "abc1234567890def",
              "spanId": "56789abcd12345",
              "parentSpanId": "1234567890abcd",
              "name": "Process HTTP GET /protected-resource",
              "kind": 3, 
              "startTimeUnixNano": "1707575201000000000",
              "endTimeUnixNano": "1707575201500000000",
              "attributes": [
                {"key": "http.method", "value": {"stringValue": "GET"}},
                {"key": "http.url", "value": {"stringValue": "/protected-resource"}},
                {"key": "http.status_code", "value": {"intValue": 200}},
                {"key": "zero_trust.token_jti", "value": {"stringValue": "token-xyz-123"}},
                {"key": "zero_trust.client_id", "value": {"stringValue": "client-abc"}},
                {"key": "processing_time_ms", "value": {"intValue": 50}}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 3.4 Wie erfolgt die Verknüpfung?
- Beide Komponenten (PEP und Resource Server) verwenden dieselbe `traceId`, die aus dem `traceparent`-Header kommt.
- Der `spanId` des HTTP-Proxies wird als `parentSpanId` im Resource Server gesetzt.
- Damit können die Traces später in OpenTelemetry-Backends wie Jaeger oder Grafana Tempo visuell zusammengeführt werden.

Damit lässt sich eine vollständige End-to-End-Tracing-Kette vom Zero Trust PEP bis zum Resource Server erstellen.

## 4. Empfehlungen

OpenTelemetry bietet eine leistungsstarke und flexible Lösung, um Performance, Last und Fehler Ihres Resource Servers in einer Zero-Trust-Architektur zu überwachen.

**Wichtige Empfehlungen:**

* **Auto-Instrumentation nutzen:** Wo immer möglich, nutzen Sie Auto-Instrumentation, um den Aufwand zu minimieren und konsistente Daten zu erhalten.
* **Attribute nutzen:** Verwenden Sie Attribute, um Metriken mit Kontextinformationen anzureichern (HTTP-Methode, Route, Statuscode, Fehlercodes).
* **Collector konfigurieren:**  Nutzen Sie den OpenTelemetry Collector, um Daten zu verarbeiten, anzureichern und an verschiedene Backends zu exportieren.
* **Backend wählen:** Wählen Sie ein geeignetes Backend für Ihre Anforderungen (Prometheus für Metriken, Jaeger/Tempo für Traces, etc.).
* **Dashboards erstellen:**  Visualisieren Sie die erfassten Metriken in Dashboards (z.B. mit Grafana), um einen Echtzeit-Überblick über den Zustand und die Performance des Resource Servers zu erhalten.
* **Alerting einrichten:**  Konfigurieren Sie Alerting-Regeln basierend auf den Metriken, um bei Problemen (z.B. hohe Latenz, hohe Fehlerrate) frühzeitig benachrichtigt zu werden.

Diese Dokumentation bietet Ihnen einen umfassenden Leitfaden zur Implementierung von OpenTelemetry Monitoring in Ihrer Zero-Trust-Umgebung. Passen Sie die Konfiguration und die Metriken an Ihre spezifischen Anforderungen an, um das bestmögliche Monitoring zu erreichen.

## 5. Anhang, OpenTelemetry Collector Deployment

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

##Backend Systems##

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

## 6. Traces und Metriken in OpenTelemetry

Ja, gerne. Dieser Trace-Ausschnitt stammt aus dem OpenTelemetry Collector und zeigt Metriken, die aus Traces generiert wurden.  Lass uns jede Zeile einzeln durchgehen, um zu verstehen, was sie bedeutet:

**Allgemeines zum Format:**

* **`2025-03-04T14:27:17.647Z        info`**: Dies ist ein Zeitstempel und der Log-Level (`info`). Es zeigt an, wann diese Information protokolliert wurde.
* **`traces.span.metrics...`**:  Dies kennzeichnet, dass es sich um Metriken handelt, die aus Spans (Teilen von Traces) generiert wurden. Der OpenTelemetry Collector kann so konfiguriert werden, dass er aus eingehenden Traces automatisch Metriken erzeugt (oft durch den `traces_to_metrics` Prozessor).
* **`{...}`**:  Innerhalb der geschweiften Klammern befinden sich Labels (Schlüssel-Wert-Paare), die die Metrik weiter beschreiben und dimensionieren.
* **`...`**:  Nach den Labels folgt der numerische Wert (oder Werte) der Metrik.

**Detaillierte Erklärung der einzelnen Zeilen:**

**1. `traces.span.metrics.calls{service.name=rs-vsdm2-app,span.name=rs-vsdm2-app.getVSDMBundle,span.kind=SPAN_KIND_SERVER,http.method=GET,http.status_code=200} 73133`**

* **Metrikname:** `traces.span.metrics.calls` - Dies ist eine Zählermetrik, die die **Anzahl der Aufrufe** (oder Spans) zählt.
* **Labels:**
    * `service.name=rs-vsdm2-app`:  Der Name des Services, der den Span erzeugt hat (hier: `rs-vsdm2-app`).
    * `span.name=rs-vsdm2-app.getVSDMBundle`: Der Name des Spans, der typischerweise die Operation oder Funktion innerhalb des Services beschreibt (hier: `rs-vsdm2-app.getVSDMBundle`).
    * `span.kind=SPAN_KIND_SERVER`:  Der Typ des Spans. `SPAN_KIND_SERVER` bedeutet, dass dieser Span einen Server-seitigen Vorgang repräsentiert, also den Empfang einer Anfrage.
    * `http.method=GET`:  Die HTTP-Methode der Anfrage (hier: `GET`).
    * `http.status_code=200`: Der HTTP-Statuscode der Antwort (hier: `200 OK`).
* **Wert:** `73133` -  Dies bedeutet, dass es im Beobachtungszeitraum **73.133 erfolgreiche `GET`-Anfragen** (Statuscode 200) an den `rs-vsdm2-app` Service für die Operation `rs-vsdm2-app.getVSDMBundle` gab.

**2. `traces.span.metrics.duration{service.name=rs-vsdm2-app,span.name=rs-vsdm2-app.getVSDMBundle,span.kind=SPAN_KIND_SERVER,http.method=GET,http.status_code=200} count=73133 sum=4942.20523000002 le0.1=65935 le1=7117 le2=66 le6=14 le10=1 le100=0 le250=0 0`**

* **Metrikname:** `traces.span.metrics.duration` - Dies ist eine Histogramm-Metrik, die die **Dauer** (Latenz) von Spans erfasst.
* **Labels:** Die Labels sind die gleichen wie in der vorherigen Zeile und beschreiben den Kontext der Duration-Metrik (Service, Span-Name, Span-Kind, HTTP-Methode, Statuscode).
* **Werte:**
    * `count=73133`:  Die **Gesamtanzahl der Spans**, die in diesem Histogramm erfasst wurden. Dies sollte mit dem Wert der `calls`-Metrik übereinstimmen (tut es hier auch).
    * `sum=4942.20523000002`: Die **Summe der Dauer aller Spans** in Sekunden (oder der in der Konfiguration verwendeten Einheit).  Hier also insgesamt ca. 4942 Sekunden.
    * `le0.1=65935`, `le1=7117`, `le2=66`, `le6=14`, `le10=1`, `le100=0`, `le250=0`:  Dies sind **Histogramm-Buckets**. `le` steht für "less than or equal to".  Jeder Bucket gibt an, **wie viele Spans eine Dauer hatten, die kleiner oder gleich dem Bucket-Wert ist**. Die Bucket-Werte sind in Sekunden angegeben (0.1s, 1s, 2s, 6s, 10s, 100s, 250s).
        * `le0.1=65935`: 65935 Spans dauerten 0.1 Sekunden oder weniger.
        * `le1=7117`: 7117 Spans dauerten zwischen 0.1 Sekunden und 1 Sekunde (73133 - 65935 - 7117 = 0,  kleiner Fehler in Addition möglich durch Rundung oder Messungenauigkeit).
        * `le2=66`: 66 Spans dauerten zwischen 1 Sekunde und 2 Sekunden.
        * ... und so weiter.
        * `le250=0`: Keine Spans dauerten länger als 250 Sekunden.
    * `0`:  Dieser letzte Wert am Ende der Zeile könnte ein impliziter Bucket für "+Inf" sein, der hier 0 ist, was bedeutet, dass keine Spans eine Dauer hatten, die größer ist als der höchste explizit definierte Bucket (250s in diesem Fall).

**Interpretation der Duration-Histogramm-Daten:**

Aus den Histogramm-Daten können wir die Latenzverteilung für die `rs-vsdm2-app.getVSDMBundle` Operation ableiten:

* Der Großteil der Anfragen (65935 von 73133) ist sehr schnell und dauert weniger als 0.1 Sekunden.
* Ein signifikanter Teil (7117) dauert zwischen 0.1 und 1 Sekunde.
* Nur sehr wenige Anfragen dauern länger als 1 Sekunde.

**3. `traces.span.metrics.calls{service.name=envoy-pep-svc,span.name=routeToRS,span.kind=SPAN_KIND_CLIENT,http.method=GET,http.status_code=200} 95853`**

* **Metrikname:** `traces.span.metrics.calls`
* **Labels:**
    * `service.name=envoy-pep-svc`:  Der Service ist hier `envoy-pep-svc`.
    * `span.name=routeToRS`: Der Span-Name ist `routeToRS`.
    * `span.kind=SPAN_KIND_CLIENT`: `SPAN_KIND_CLIENT` deutet darauf hin, dass dieser Span einen Client-seitigen Vorgang repräsentiert, also das **Senden** einer Anfrage (z.B. von `envoy-pep-svc` an einen anderen Service).
    * `http.method=GET`: HTTP-Methode `GET`.
    * `http.status_code=200`: HTTP-Statuscode `200`.
* **Wert:** `95853` - Es gab 95.853 erfolgreiche `GET`-Anfragen des `envoy-pep-svc` Services für die Operation `routeToRS`.

**4. `traces.span.metrics.duration{service.name=envoy-pep-svc,span.name=routeToRS,span.kind=SPAN_KIND_CLIENT,http.method=GET,http.status_code=200} count=95853 sum=55005.53899999984 le0.1=0 le1=91068 le2=4285 le6=482 le10=13 le100=2 le250=0 3`**

* **Metrikname:** `traces.span.metrics.duration`
* **Labels:** Wie in Zeile 3, aber für den `envoy-pep-svc` Service und die `routeToRS` Operation.
* **Werte:**
    * `count=95853`: Anzahl der Spans, stimmt mit der `calls`-Metrik überein.
    * `sum=55005.53899999984`:  Summe der Dauer aller Spans (ca. 55005 Sekunden).
    * `le0.1=0`: Keine Spans dauerten weniger als 0.1 Sekunden.
    * `le1=91068`: 91068 Spans dauerten 1 Sekunde oder weniger.
    * `le2=4285`: 4285 Spans dauerten zwischen 1 und 2 Sekunden.
    * ...Histogramm-Buckets bis `le250=0`.
    * `3`:  Impliziter "+Inf" Bucket mit Wert 3.  Hier gibt es **3 Spans, die länger als 250 Sekunden dauerten**.

**Interpretation der Duration für `envoy-pep-svc.routeToRS`:**

* Im Gegensatz zu `rs-vsdm2-app.getVSDMBundle` sind hier **keine** Anfragen unter 0.1 Sekunden.
* Der Großteil der Anfragen (91068 von 95853) dauert bis zu 1 Sekunde.
* Es gibt eine signifikante Anzahl, die zwischen 1 und 2 Sekunden dauern (4285).
* Es gibt sogar 3 Anfragen, die extrem lange dauern (über 250 Sekunden).

**5. `{"otelcol.component.id": "debug", "otelcol.component.kind": "Exporter", "otelcol.signal": "metrics"}`**

* Dies ist **keine Metrik**, sondern ein **Log-Eintrag** des OpenTelemetry Collectors selbst.
* **Labels:**
    * `otelcol.component.id": "debug"`:  Die ID der Komponente ist "debug".
    * `otelcol.component.kind": "Exporter"`: Der Komponententyp ist "Exporter".
    * `otelcol.signal": "metrics"`:  Das Signal, das von dieser Komponente behandelt wird, sind "metrics".
* **Bedeutung:** Diese Zeile deutet darauf hin, dass der "debug" Exporter (wahrscheinlich ein Debug- oder Logging-Exporter innerhalb des OTel Collectors) Metrikdaten verarbeitet hat.  Es ist eine interne Log-Nachricht des Collectors und liefert keine Informationen über die Anwendungs-Metriken selbst.

**Zusammenfassende Erläuterung:**

Der Trace-Ausschnitt zeigt Metriken, die aus Traces für zwei Services (`rs-vsdm2-app` und `envoy-pep-svc`) generiert wurden.  Er liefert Informationen über die Anzahl der Aufrufe und die Latenzverteilung für bestimmte Operationen (`getVSDMBundle` und `routeToRS`) mit dem HTTP-Methode `GET` und dem Statuscode `200`.

**Wichtige Erkenntnisse:**

* **`rs-vsdm2-app.getVSDMBundle` ist sehr schnell:** Die meisten Anfragen sind unter 0.1 Sekunden.
* **`envoy-pep-svc.routeToRS` ist langsamer und variabler:**  Die Latenzen sind höher und breiter verteilt, mit einigen Ausreißern, die sehr lange dauern. Dies könnte ein Hinweis auf potenzielle Performance-Probleme oder Engpässe im `envoy-pep-svc` Service oder in der `routeToRS` Operation sein, die genauer untersucht werden sollten.
* **Unterschiedliche Span-Kinds:**  Es wird zwischen `SPAN_KIND_SERVER` (eingehende Anfragen für `rs-vsdm2-app`) und `SPAN_KIND_CLIENT` (ausgehende Anfragen von `envoy-pep-svc`) unterschieden, was Einblicke in den Request-Flow gibt.

Diese Metriken können in Prometheus und Grafana verwendet werden, um Dashboards und Alarme zu erstellen, um die Gesundheit und Performance Ihrer Anwendungen zu überwachen.

## 7. OpenTelemetry Collector Konfiguration Abschnitt für Abschnitt


**Grundstruktur der Konfiguration:**

Die Konfiguration ist in verschiedene Abschnitte unterteilt, die die Funktionalität des Collectors definieren:

*   **`receivers`**: Definieren, wie der Collector Daten empfängt (z.B. von Applikationen, anderen Collectoren).
*   **`exporters`**: Definieren, wohin der Collector die verarbeiteten Daten exportiert (z.B. Prometheus, Jaeger, Logging).
*   **`processors`**: Definieren, wie die Daten *verarbeitet* werden, bevor sie exportiert werden (z.B. Batching, Attribut-Manipulation).
*   **`connectors`**: Spezialisierte Komponenten, die Datenströme verbinden oder transformieren. `spanmetrics` ist ein Connector, der Traces in Metriken umwandelt.
*   **`service`**: Definiert die Pipelines, die die Datenflüsse durch den Collector steuern. Pipelines verbinden Receivers, Processors und Exporters.

**Detaillierte Erklärung der Abschnitte:**

**1. `receivers`:**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"
```

*   **`otlp`**: Dies ist der `otlp` (OpenTelemetry Protocol) Receiver. Er ermöglicht dem Collector, Telemetriedaten im OTLP-Format zu empfangen.
*   **`protocols`**: Definiert die Protokolle, die der `otlp` Receiver unterstützt.
    *   **`grpc`**: Aktiviert den gRPC-Protokoll-Empfang.
        *   **`endpoint: "0.0.0.0:4317"`**:  Legt fest, dass der Collector auf allen Netzwerkschnittstellen (`0.0.0.0`) auf Port `4317` für gRPC-Verbindungen lauscht. Dies ist der Standardport für OTLP/gRPC.
    *   **`http`**: Aktiviert den HTTP-Protokoll-Empfang (für OTLP/HTTP).
        *   **`endpoint: "0.0.0.0:4318"`**: Legt fest, dass der Collector auf allen Netzwerkschnittstellen auf Port `4318` für HTTP-Verbindungen lauscht. Dies ist der Standardport für OTLP/HTTP.

**Zusammenfassend für `receivers`**: Der Collector ist so konfiguriert, dass er OTLP-Daten über gRPC auf Port 4317 und über HTTP auf Port 4318 empfangen kann. Anwendungen oder andere OTel-Komponenten können Traces, Metriken und Logs an diese Endpunkte senden.

**2. `exporters`:**

```yaml
exporters:
  prometheus:
    endpoint: "0.0.0.0:9090"
  otlp/jaeger:
    endpoint: "jaeger-svc:4317"
    tls:
      insecure: true
  debug:
    verbosity: normal
```

*   **`prometheus`**: Dies ist der `prometheus` Exporter. Er macht Metriken, die der Collector verarbeitet, in einem Format verfügbar, das Prometheus scrapen kann.
    *   **`endpoint: "0.0.0.0:9090"`**: Der Prometheus Exporter stellt seine Metriken unter `http://<collector-ip>:9090/metrics` bereit. Prometheus kann diesen Endpoint scrapen, um die Metriken zu sammeln.
*   **`otlp/jaeger`**: Dies ist der `otlp` Exporter, der speziell für den Export von Traces an Jaeger konfiguriert ist.
    *   **`endpoint: "jaeger-svc:4317"`**:  Der Collector sendet Traces an den Jaeger Agent (oder Collector) unter der Adresse `jaeger-svc:4317`.  `jaeger-svc` ist hier wahrscheinlich ein DNS-Name oder ein Service-Name in einem Container-Orchestrierungssystem wie Kubernetes, der zum Jaeger Service auflöst. Port `4317` ist der Standardport für OTLP/gRPC für Jaeger.
    *   **`tls`**: Konfiguration für TLS (Transport Layer Security) Verschlüsselung.
        *   **`insecure: true`**:  Deaktiviert die TLS-Zertifikatsverifizierung. **Achtung**: Dies sollte in Produktionsumgebungen vermieden werden, da es die Sicherheit beeinträchtigt. Für Testumgebungen kann es akzeptabel sein.
*   **`debug`**: Dies ist der `debug` Exporter. Er ist nützlich für das Debugging und die Protokollierung.
    *   **`verbosity: normal`**:  Legt die Ausführlichkeit der Debug-Ausgaben auf "normal" fest. Der Debug Exporter wird Informationen in die Collector-Logs schreiben, was bei der Fehlersuche hilfreich sein kann.

**Zusammenfassend für `exporters`**: Der Collector ist konfiguriert, um:
    *   Metriken für Prometheus unter Port 9090 bereitzustellen.
    *   Traces an Jaeger unter `jaeger-svc:4317` (unsicher über TLS) zu exportieren.
    *   Debug-Informationen in die Logs zu schreiben.

**3. `processors`:**

```yaml
processors:
  batch:
```

*   **`batch`**: Dies ist der `batch` Prozessor. Er optimiert den Export von Telemetriedaten, indem er mehrere Datenpunkte (Spans, Metriken, Logs) in Batches zusammenfasst und sie dann effizienter exportiert. Dies reduziert die Last auf die Exporter und die Zielsysteme, besonders bei hohem Durchsatz.
*   **Keine weiteren Konfigurationsparameter**: In dieser einfachen Konfiguration sind keine weiteren Parameter für den `batch` Prozessor angegeben, was bedeutet, dass die Standardeinstellungen verwendet werden.  Standardmäßig wird der Batch-Prozessor Daten basierend auf der Anzahl der Elemente oder der verstrichenen Zeit batchen.

**Zusammenfassend für `processors`**: Der Collector verwendet einen Batch-Prozessor, um die Effizienz des Datenexports zu verbessern.

**4. `connectors`:**

```yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [100us, 1ms, 2ms, 6ms, 10ms, 100ms, 250ms]
    dimensions:
      - name: http.method
        default: GET
      - name: http.status_code
    exemplars:
      enabled: true
    exclude_dimensions: ['status.code']
    dimensions_cache_size: 1000
    aggregation_temporality: "AGGREGATION_TEMPORALITY_CUMULATIVE"
    metrics_flush_interval: 15s
    metrics_expiration: 60m
    events:
      enabled: true
      dimensions:
        - name: exception.type
        - name: exception.message
    resource_metrics_key_attributes:
      - service.name
      - telemetry.sdk.language
      - telemetry.sdk.name
```

*   **`spanmetrics`**: Dies ist der `spanmetrics` Connector. Er ist **zentral für die Generierung von Metriken aus Traces**. Er analysiert eingehende Traces und erzeugt daraus Metriken, die dann weiterverarbeitet und exportiert werden können.
    *   **`histogram`**: Konfiguration für Histogramm-Metriken (z.B. für Latenz).
        *   **`explicit`**:  Definiert die Histogramm-Buckets explizit.
            *   **`buckets: [100us, 1ms, 2ms, 6ms, 10ms, 100ms, 250ms]`**:  Legt die Bucket-Grenzen für die Histogramme fest.  Diese Buckets sind in aufsteigender Reihenfolge und definieren die Bereiche für die Latenzmessungen (100 Mikrosekunden, 1 Millisekunde, 2ms, 6ms, 10ms, 100ms, 250ms).  Der Connector generiert Histogramm-Metriken wie `traces.span.metrics.duration` mit diesen Buckets.
    *   **`dimensions`**: Definiert, welche Span-Attribute als Dimensionen (Labels) für die generierten Metriken verwendet werden sollen.
        *   **`- name: http.method`**:  Das Span-Attribut `http.method` wird als Dimension verwendet.
            *   **`default: GET`**: Wenn `http.method` im Span nicht vorhanden ist, wird der Default-Wert `GET` verwendet.
        *   **`- name: http.status_code`**: Das Span-Attribut `http.status_code` wird als Dimension verwendet.
    *   **`exemplars`**: Konfiguration für Exemplare.
        *   **`enabled: true`**: Aktiviert die Erfassung von Exemplaren. Exemplare sind Beispiel-Traces, die zu bestimmten Histogramm-Buckets gehören. Sie helfen, die Verteilung der Metriken besser zu verstehen, indem sie konkrete Trace-IDs zu langsamen Anfragen liefern.
    *   **`exclude_dimensions: ['status.code']`**:  Schließt die Dimension `status.code` von den generierten Metriken aus.  Eventuell redundant, da `status.code` in HTTP Kontext oft durch `http.status_code` abgedeckt ist.
    *   **`dimensions_cache_size: 1000`**: Legt die Größe des Caches für Dimensionen auf 1000 Einträge fest. Dies kann die Performance verbessern, besonders bei einer großen Anzahl unterschiedlicher Dimensionskombinationen.
    *   **`aggregation_temporality: "AGGREGATION_TEMPORALITY_CUMULATIVE"`**:  Setzt die Aggregationstemporalität auf "Cumulative".  Dies ist der Standard und typisch für Prometheus. Cumulative-Metriken repräsentieren einen Wert, der über die gesamte Lebensdauer des Prozesses ansteigt (z.B. Gesamtzahl der Anfragen, Summe der Latenzen).
    *   **`metrics_flush_interval: 15s`**:  Legt das Intervall fest, in dem die `spanmetrics` Connector seine gesammelten Metriken "flusht" (exportiert). Hier alle 15 Sekunden.
    *   **`metrics_expiration: 60m`**:  Legt die Gültigkeitsdauer für Metriken im internen Cache auf 60 Minuten fest. Metriken, die älter als 60 Minuten sind, werden verworfen.
    *   **`events`**: Konfiguration für die Generierung von Metriken aus Span-Events.
        *   **`enabled: true`**: Aktiviert die Event-Metrik-Generierung.
        *   **`dimensions`**: Definiert Dimensionen für Event-Metriken.
            *   **`- name: exception.type`**:  Verwendet das Event-Attribut `exception.type` als Dimension.
            *   **`- name: exception.message`**: Verwendet das Event-Attribut `exception.message` als Dimension.  Dies ermöglicht es, Metriken zu aggregieren und zu filtern basierend auf Exception-Typen und -Nachrichten, die in Spans als Events erfasst werden.
    *   **`resource_metrics_key_attributes`**: Definiert Resource-Attribute, die als zusätzliche Dimensionen zu den generierten Metriken hinzugefügt werden sollen.
        *   **`- service.name`**: Fügt das Resource-Attribut `service.name` als Dimension hinzu.
        *   **`- telemetry.sdk.language`**: Fügt das Resource-Attribut `telemetry.sdk.language` hinzu (z.B. "java", "python").
        *   **`- telemetry.sdk.name`**: Fügt das Resource-Attribut `telemetry.sdk.name` hinzu (z.B. "opentelemetry").  Diese Resource-Attribute helfen, die Herkunft der Metriken genauer zu identifizieren.

**Zusammenfassend für `connectors.spanmetrics`**: Dieser Connector ist sehr detailliert konfiguriert, um aus eingehenden Traces Histogramm- und Event-Metriken zu generieren.  Er extrahiert wichtige Dimensionen aus Spans (HTTP-Methode, Statuscode, Exception-Details) und fügt Resource-Attribute hinzu, um die resultierenden Metriken reichhaltig und analysierbar zu machen. Die Histogramm-Buckets sind für typische Latenzbereiche definiert.

**5. `service.pipelines`:**

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]  # <-----  CRITICAL: batch processor IS in traces pipeline
      exporters: [spanmetrics, debug, otlp/jaeger] # <----- CRITICAL: spanmetrics is in traces pipeline EXPORTERS (as connector)
    metrics:
      receivers: [spanmetrics, otlp]
      processors: [batch]
      exporters: [prometheus, debug]
```

*   **`service`**: Definiert die Services des Collectors (in diesem Fall nur Pipelines).
    *   **`pipelines`**: Definiert die Datenpipelines.
        *   **`traces`**: Definiert die Trace-Pipeline.
            *   **`receivers: [otlp]`**:  Die Trace-Pipeline empfängt Daten vom `otlp` Receiver (wie oben konfiguriert).
            *   **`processors: [batch]`**:  Die Trace-Daten werden durch den `batch` Prozessor geleitet.
            *   **`exporters: [spanmetrics, debug, otlp/jaeger]`**:  Die Trace-Daten (und die daraus generierten Metriken vom `spanmetrics` Connector!) werden an folgende Exporter gesendet:
                *   **`spanmetrics`**:  **Wichtig:**  Hier wird der `spanmetrics` Connector als *Exporter* in der `traces`-Pipeline aufgeführt. Das ist **nicht** korrekt im Sinne eines typischen Exporters. In diesem Kontext fungiert `spanmetrics` **eher als ein Prozessor, der Metriken *erzeugt*, aber diese Metriken werden dann innerhalb des Collectors weitergeleitet**. Die generierten Metriken fließen dann in die `metrics`-Pipeline (siehe unten).  **Es ist wichtig zu verstehen, dass `spanmetrics` hier *in der Trace-Pipeline* ist, um *aus Traces Metriken zu generieren***.
                *   **`debug`**:  Traces werden auch an den `debug` Exporter gesendet (für Logging).
                *   **`otlp/jaeger`**: Traces werden auch an den `otlp/jaeger` Exporter gesendet (um sie an Jaeger zu exportieren).
        *   **`metrics`**: Definiert die Metrik-Pipeline.
            *   **`receivers: [spanmetrics, otlp]`**: Die Metrik-Pipeline empfängt Daten von:
                *   **`spanmetrics`**: **Wichtig:** Hier wird `spanmetrics` als *Receiver* in der `metrics`-Pipeline aufgeführt.  Dies bedeutet, dass die Metriken, die der `spanmetrics` Connector in der `traces`-Pipeline *generiert* hat, **hier als Input für die Metrik-Pipeline dienen**.
                *   **`otlp`**:  Die Metrik-Pipeline empfängt auch Metriken direkt vom `otlp` Receiver.  Dies ermöglicht es dem Collector, sowohl direkt von Anwendungen gesendete Metriken (über OTLP) als auch Metriken, die aus Traces generiert wurden, zu verarbeiten.
            *   **`processors: [batch]`**:  Die Metrik-Daten werden durch den `batch` Prozessor geleitet.
            *   **`exporters: [prometheus, debug]`**: Die Metrik-Daten werden an folgende Exporter gesendet:
                *   **`prometheus`**: Metriken werden an den `prometheus` Exporter gesendet (um sie für Prometheus verfügbar zu machen).
                *   **`debug`**: Metriken werden auch an den `debug` Exporter gesendet (für Logging).

**Zusammenfassend für `service.pipelines`**:

*   **Trace-Pipeline**: Empfängt Traces über OTLP, batched sie, generiert Metriken aus ihnen mit dem `spanmetrics` Connector, loggt Traces und exportiert Traces nach Jaeger.
*   **Metrik-Pipeline**: Empfängt Metriken, die vom `spanmetrics` Connector generiert wurden (aus Traces) und direkt über OTLP empfangene Metriken, batched sie, loggt Metriken und exportiert sie nach Prometheus.

**Wichtige Punkte und Zusammenhänge:**

*   **`spanmetrics` als Connector und Pipeline-Komponente**:  `spanmetrics` ist ein Connector, der *innerhalb* der Trace-Pipeline als Exporter gelistet ist.  Es erzeugt Metriken aus Traces und leitet diese intern an die Metrik-Pipeline weiter.  Es ist **kein** typischer Exporter, der Daten an ein externes System sendet, sondern ein **Transformationsschritt innerhalb des Collectors**.
*   **Datenfluss**: Traces kommen über den `otlp` Receiver in die Trace-Pipeline. Der `spanmetrics` Connector in der Trace-Pipeline generiert daraus Metriken. Diese Metriken werden dann in der Metrik-Pipeline zusammen mit direkt empfangenen OTLP-Metriken verarbeitet und an Prometheus exportiert. Traces selbst werden an Jaeger und den Debug-Exporter exportiert.
*   **Metrik-Generierung aus Traces**: Diese Konfiguration demonstriert, wie man mit dem `spanmetrics` Connector automatisch wertvolle Metriken aus den Traces generieren kann, ohne dass Anwendungen explizit Metriken instrumentieren müssen. Dies ist ein sehr mächtiges Feature des OpenTelemetry Collectors.

Diese Konfiguration ist ein gutes Beispiel für einen OTel Collector, der Traces und Metriken verarbeitet, Metriken aus Traces generiert und die Daten an verschiedene Backend-Systeme (Prometheus, Jaeger) exportiert, während er gleichzeitig Debugging-Möglichkeiten bietet.

## 8. Referenzen

1. [OpenTelemetry Homepage](https://opentelemetry.io/)
2. [OpenTelemetry Cookbook](https://www.youtube.com/watch?v=UGTU0-KT_60)
3. [OpenTelemetry Transformation Language](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/ottl/README.md)