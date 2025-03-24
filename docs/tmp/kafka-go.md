# Kafka und OpenTelemetry

## Kafka

**Apache Kafka** ist eine verteilte Streaming-Plattform bzw. ein verteilter Message-Broker, der hauptsächlich für das **Publish-Subscribe-Modell** verwendet wird. Es wurde von LinkedIn entwickelt und später an die Apache Software Foundation übergeben.

Mit Kafka können große Mengen von Ereignisdaten (Logs, Metriken, Messages) **in Echtzeit** zwischen Produzenten (z.B. Anwendungen, Dienste) und Konsumenten (z.B. Datenbanken, Analyse-Tools, Microservices) transportiert werden.

---

### Kafka - Hauptfunktionen

1. **Message Broker**  
   Kafka nimmt Daten von einem „Producer“ entgegen und stellt sie einem oder mehreren „Consumer“-Systemen bereit.

2. **Distributed Log Storage**  
   Kafka speichert die Events in sogenannten **Topics** als unveränderliche Logs und kann sie über längere Zeiträume (von Stunden bis Monaten) abrufbar halten.

3. **Streaming-Engine**  
   Kafka ist nicht nur Messaging, sondern erlaubt auch **Stream Processing** mit Kafka Streams oder externen Tools wie ksqlDB oder Apache Flink.

---

### Wichtige Kafka-Konzepte

| Begriff       | Beschreibung |
|---------------|--------------|
| **Producer**  | Komponente, die Daten (Events, Nachrichten) in Kafka schreibt. |
| **Consumer**  | Komponente, die Daten aus Kafka liest. |
| **Topic**     | Eine Art "Kanal" oder "Kategorie", in dem Kafka Nachrichten speichert. |
| **Partition** | Ein Topic kann in Partitionen aufgeteilt werden, um parallelisierbar und skalierbar zu sein. |
| **Broker**    | Ein einzelner Kafka-Server. Mehrere Broker zusammen bilden einen Kafka-Cluster. |
| **ZooKeeper** | Früher notwendige Komponente für Kafka zur Koordination, mittlerweile oft ersetzt durch **KRaft (Kafka Raft Metadata Mode)**. |

---

### Typische Anwendungsfälle

- **Log Aggregation** (ähnlich wie bei Logstash oder Fluentd)
- **Event-Streaming** (z.B. für IoT, Payments, Sensor-Daten)
- **Microservice-Kommunikation** (asynchron über Kafka Topics)
- **ETL Pipelines** (Kafka → Stream Processing → Data Warehouse)
- **Real-Time Analytics**

---

### Besondere Eigenschaften

- **Hoch skalierbar** (horizontal über Partitionen & Broker)
- **Sehr hohe Durchsatzraten** (Millionen von Events pro Sekunde)
- **Persistenz** der Daten (Daten können nach Tagen oder Wochen noch gelesen werden)
- **Fehlertolerant** (Replikation von Partitionen auf mehrere Broker)

---

## Kafka in go

Um ein vorhandenes **Go-Programm** als **Kafka Producer** oder **Consumer** zu instrumentieren, nutzt man in der Regel die populäre Kafka-Client-Bibliothek für Go, z. B. **[confluent-kafka-go](https://github.com/confluentinc/confluent-kafka-go)** oder **[segmentio/kafka-go](https://github.com/segmentio/kafka-go)**.

---

### Variante 1: Mit `segmentio/kafka-go` (rein Go-basiert)

#### Producer-Beispiel

```go
import (
    "context"
    "github.com/segmentio/kafka-go"
    "log"
)

func main() {
    writer := kafka.NewWriter(kafka.WriterConfig{
        Brokers: []string{"localhost:9092"},
        Topic:   "my-topic",
    })
    defer writer.Close()

    err := writer.WriteMessages(context.Background(),
        kafka.Message{
            Key:   []byte("key1"),
            Value: []byte("Hello Kafka!"),
        },
    )
    if err != nil {
        log.Fatal("failed to write messages:", err)
    }
    log.Println("Message sent!")
}
```

#### Consumer-Beispiel

```go
import (
    "context"
    "github.com/segmentio/kafka-go"
    "log"
)

func main() {
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: []string{"localhost:9092"},
        GroupID: "my-group",
        Topic:   "my-topic",
    })
    defer reader.Close()

    for {
        msg, err := reader.ReadMessage(context.Background())
        if err != nil {
            log.Fatal(err)
        }
        log.Printf("received: key=%s value=%s", string(msg.Key), string(msg.Value))
    }
}
```

---

### Variante 2: Mit `confluent-kafka-go` (C-Binding zu librdkafka)

#### Producer-Beispiel

```go
import (
    "github.com/confluentinc/confluent-kafka-go/kafka"
    "log"
)

func main() {
    p, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": "localhost:9092"})
    if err != nil {
        panic(err)
    }
    defer p.Close()

    topic := "my-topic"
    err = p.Produce(&kafka.Message{
        TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
        Key:            []byte("key1"),
        Value:          []byte("Hello Kafka!"),
    }, nil)
    if err != nil {
        log.Fatal(err)
    }

    // Optional: Events abfangen (z.B. Delivery Reports)
    go func() {
        for e := range p.Events() {
            switch ev := e.(type) {
            case *kafka.Message:
                if ev.TopicPartition.Error != nil {
                    log.Printf("Delivery failed: %v\n", ev.TopicPartition)
                } else {
                    log.Printf("Delivered to %v\n", ev.TopicPartition)
                }
            }
        }
    }()
    p.Flush(5000)
}
```

#### Consumer-Beispiel:

```go
import (
    "github.com/confluentinc/confluent-kafka-go/kafka"
    "log"
)

func main() {
    c, err := kafka.NewConsumer(&kafka.ConfigMap{
        "bootstrap.servers": "localhost:9092",
        "group.id":          "my-group",
        "auto.offset.reset": "earliest",
    })
    if err != nil {
        panic(err)
    }
    defer c.Close()

    c.SubscribeTopics([]string{"my-topic"}, nil)

    for {
        msg, err := c.ReadMessage(-1)
        if err == nil {
            log.Printf("Received message: %s: %s\n", string(msg.Key), string(msg.Value))
        } else {
            log.Printf("Consumer error: %v (%v)\n", err, msg)
        }
    }
}
```

---

### Kafka Instrumentierung

1. **Kafka Writer/Reader oder Producer/Consumer als Package importieren**
   - Typischerweise in den Bereichen, wo du Logs, Events oder Daten erzeugst oder empfangen möchtest.
   
2. **Kafka-Config konfigurierbar machen (über `config.yaml` oder ENV-Variablen)**

3. **Eventuelle Serialisierung/Deserialisierung (JSON, Protobuf, Avro)** integrieren.

4. **Optional: OpenTelemetry Tracing hinzufügen**, falls du Kafka-Producing/Consuming auch observieren möchtest.

---

## OpenTelemetry und Kafka

Der **OpenTelemetry Collector** kann direkt als **Kafka Consumer** arbeiten und von einem Kafka-Topic aus Daten empfangen, die dann innerhalb der OpenTelemetry-Pipeline weiterverarbeitet und exportiert werden.

---

### Integration von Kafka und OpenTelemetry

Der Collector bietet ein fertiges **kafka receiver** Modul an, das es ermöglicht, Traces, Logs oder Metrics direkt aus Kafka zu konsumieren.

---

### Beispiel: OTEL Collector als Kafka-Consumer

```yaml
receivers:
  kafka:
    brokers:
      - "kafka-broker1:9092"
      - "kafka-broker2:9092"
    topic: "otel-logs"
    encoding: "otlp_json"  # oder "otlp_proto", je nach Producer
    group_id: "otel-collector-group"

processors:
  batch: {}

exporters:
  logging:  # zu Debugging-Zwecken
    loglevel: debug

service:
  pipelines:
    logs:
      receivers: [kafka]
      processors: [batch]
      exporters: [logging]
```

---

### Ablauf
- Der Collector tritt als **Consumer** einer Kafka-Topic bei (hier `otel-logs`).
- Er verarbeitet die empfangenen OTLP-Logs (z.B. als JSON oder Protobuf) weiter.
- Die Daten können dann mit beliebigen Exportern z.B. zu **Grafana Loki**, **Elasticsearch**, **Splunk**, **OTLP** oder anderen Tools gesendet werden.

---

### Unterstützte Payloads im Kafka Receiver
- `otlp_proto`
- `otlp_json`
- `jaeger_proto`
- `zipkin_proto`
- Custom payloads via Kafka Encoding + Decoder.

---

### Kafka go Client für OTLP/gRPC Logs

Hier folgt ein **Kafka Producer**-Beispiel in Go, dass **OTLP/gRPC Logs** verschickt.

Workflow:

1. Der **Go-Producer** erzeugt Log-Daten im **OTLP gRPC Format** und sendet sie **über Kafka**.
2. Der **otel-collector Consumer** liest die Kafka-Nachricht und verarbeitet die Logs direkt in den Pipelines.

---

#### 📦 Dependencies
```bash
go get github.com/segmentio/kafka-go
go get go.opentelemetry.io/proto/otlp/logs/v1
go get google.golang.org/protobuf/proto
```

#### Producer Beispiel:

```go
package main

import (
    "context"
    "log"

    "github.com/segmentio/kafka-go"
    logsproto "go.opentelemetry.io/proto/otlp/logs/v1"
    "google.golang.org/protobuf/proto"
)

func main() {
    // Kafka Writer
    writer := kafka.NewWriter(kafka.WriterConfig{
        Brokers: []string{"localhost:9092"},
        Topic:   "otel-logs",
    })
    defer writer.Close()

    // OTLP LogRecord erstellen
    logRecord := &logsproto.LogRecord{
        SeverityText: "INFO",
        Body:         &logsproto.AnyValue{Value: &logsproto.AnyValue_StringValue{StringValue: "Hello OTLP via Kafka"}},
    }

    // OTLP als protobuf serialisieren
    payload, err := proto.Marshal(logRecord)
    if err != nil {
        log.Fatal("protobuf marshal error:", err)
    }

    // Kafka Message senden
    err = writer.WriteMessages(context.Background(), kafka.Message{
        Key:   []byte("log-key"),
        Value: payload,
    })
    if err != nil {
        log.Fatal("kafka write error:", err)
    }
    log.Println("OTLP log sent to Kafka")
}
```

---

#### ✅ Ergebnis
- **Producer:** schickt OTLP-Logs als Protobuf direkt nach Kafka.
- **Consumer:** (otel-collector) liest aus Kafka und verarbeitet die Daten.

---

