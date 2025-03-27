package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/schollz/progressbar/v3" // go get github.com/schollz/progressbar/v3
)

var (
	targetRPS    = flag.Int("rps", 4000, "Ziel-Requests pro Sekunde (gesamt)")
	duration     = flag.Int("duration", 10, "Dauer des Tests in Sekunden")
	targetURL    = flag.String("url", "http://localhost/vsdservice/v1/vsdmbundle", "Ziel URL")
	threads      = flag.Int("threads", 64, "Anzahl paralleler Worker (Goroutinen)")
	showProgress = flag.Bool("progress", true, "Zeige Fortschrittsanzeige an")
)

var (
	requestCounter uint64 // Zähler für gesendete Requests (atomar)
	errorCounter   uint64 // Zähler für fehlerhafte Requests (atomar)
)

func main() {
	flag.Parse()

	if *targetRPS <= 0 || *duration <= 0 || *threads <= 0 || *targetURL == "" {
		fmt.Println("Ungültige Argumente. RPS, Duration und Threads müssen > 0 sein, URL darf nicht leer sein.")
		flag.Usage()
		os.Exit(1)
	}

	// --- Optimierten HTTP Client erstellen ---
	// Angepasst für hohe Last und niedrige Latenz
	httpClient := &http.Client{
		Timeout: 10 * time.Second, // Gesamter Timeout pro Request
		Transport: &http.Transport{
			Proxy: http.ProxyFromEnvironment,
			DialContext: (&net.Dialer{
				Timeout:   2 * time.Second, // Connection Timeout
				KeepAlive: 30 * time.Second,
			}).DialContext,
			MaxIdleConns:        *threads * 2, // Mehr Idle Connections erlauben
			MaxIdleConnsPerHost: *threads * 2, // Mehr Idle Connections pro Host
			IdleConnTimeout:     90 * time.Second,
			TLSHandshakeTimeout: 5 * time.Second,
			// ExpectContinueTimeout: 1 * time.Second, // Kann helfen, muss aber serverseitig unterstützt werden
			ForceAttemptHTTP2: true, // Versuche HTTP/2 wenn möglich
			// ResponseHeaderTimeout: 5 * time.Second, // Timeout für das Warten auf Header nach dem Senden
		},
	}

	// --- Kontext für Dauersteuerung ---
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(*duration)*time.Second)
	defer cancel() // Sicherstellen, dass der Kontext am Ende gecancelt wird

	var wg sync.WaitGroup

	// --- RPS pro Worker berechnen ---
	// Verwende float64 für genauere Verteilung, aber mindestens 1 RPS pro Thread (falls Gesamt-RPS < Threads)
	rpsPerWorker := float64(*targetRPS) / float64(*threads)
	if rpsPerWorker < 1.0 && *targetRPS > 0 {
		rpsPerWorker = 1.0 // Mindestens 1 RPS pro Worker, wenn RPS angefordert
	}

	fmt.Printf("Starte Load Test...\n")
	fmt.Printf("  URL:         %s\n", *targetURL)
	fmt.Printf("  Threads:     %d\n", *threads)
	fmt.Printf("  RPS (Ziel):  %d (ca. %.2f pro Thread)\n", *targetRPS, rpsPerWorker)
	fmt.Printf("  Dauer:       %d s\n", *duration)
	fmt.Println("------------------------------------")

	// --- Fortschrittsanzeige Initialisieren ---
	totalExpectedRequests := int64(*targetRPS * *duration)
	bar := progressbar.NewOptions64(
		totalExpectedRequests,
		progressbar.OptionSetDescription("Fortschritt"),
		progressbar.OptionSetWriter(os.Stderr), // Schreibe in Stderr, um stdout für Ergebnisse freizuhalten
		progressbar.OptionSetWidth(40),
		progressbar.OptionThrottle(100*time.Millisecond), // Nicht zu oft aktualisieren
		progressbar.OptionShowCount(),
		progressbar.OptionShowIts(), // Zeigt Rate (items/sec)
		progressbar.OptionSpinnerType(14),
		progressbar.OptionFullWidth(),
		progressbar.OptionSetPredictTime(false), // Vorhersage ist bei variabler Rate nicht sinnvoll
		progressbar.OptionClearOnFinish(),       // Löscht die Leiste nach Abschluss
	)
	if !*showProgress {
		bar = progressbar.New(0) // Dummy-Bar, wenn nicht angezeigt
	}

	// --- Goroutine für periodische Fortschrittsaktualisierung ---
	var progressWg sync.WaitGroup
	if *showProgress {
		progressWg.Add(1)
		go func() {
			defer progressWg.Done()
			ticker := time.NewTicker(5 * time.Second) // Alle 5 Sekunden aktualisieren
			defer ticker.Stop()

			for {
				select {
				case <-ticker.C:
					currentRequests := atomic.LoadUint64(&requestCounter)
					_ = bar.Set64(int64(currentRequests)) // Fehler ignorieren, Set64 ist robust
				case <-ctx.Done(): // Wenn der Hauptkontext endet
					currentRequests := atomic.LoadUint64(&requestCounter)
					_ = bar.Set64(int64(currentRequests)) // Letztes Update
					return
				}
			}
		}()
	}

	// --- Worker Goroutinen starten ---
	startTime := time.Now()
	for i := 0; i < *threads; i++ {
		wg.Add(1)
		go worker(ctx, &wg, httpClient, *targetURL, rpsPerWorker, i)
	}

	// --- Warten bis alle Worker fertig sind ODER die Zeit abgelaufen ist ---
	// Das ctx.Done() Signal sorgt dafür, dass Worker aufhören.
	// wg.Wait() stellt sicher, dass wir auf alle gestoppten Worker warten, bevor wir weitermachen.
	wg.Wait()

	// --- Test Ende ---
	elapsedTime := time.Since(startTime)

	// Stelle sicher, dass der Progress-Updater beendet ist
	cancel() // Signalisiere dem Updater explizit das Ende (obwohl Timeout dies auch tut)
	if *showProgress {
		progressWg.Wait() // Warte auf den Updater
		_ = bar.Finish()  // Schließe die Progressbar sauber ab
	}

	// --- Ergebnisse sammeln ---
	finalRequests := atomic.LoadUint64(&requestCounter)
	finalErrors := atomic.LoadUint64(&errorCounter)
	actualRPS := float64(finalRequests) / elapsedTime.Seconds()

	// Korrektur, falls Laufzeit extrem kurz war (verhindert NaN/Inf)
	if elapsedTime.Seconds() == 0 {
		actualRPS = 0
	}

	// --- Zusammenfassung ausgeben ---
	fmt.Println("\n--- Load Test Zusammenfassung ---")
	fmt.Printf("Ziel URL:           %s\n", *targetURL)
	fmt.Printf("Geplante RPS:       %d\n", *targetRPS)
	fmt.Printf("Geplante Dauer:     %d Sekunden\n", *duration)
	fmt.Printf("Anzahl Threads:     %d\n", *threads)
	fmt.Printf("Tatsächliche Dauer: %.2f Sekunden\n", elapsedTime.Seconds())
	fmt.Printf("Gesendete Requests: %d\n", finalRequests)
	fmt.Printf("Fehlerhafte Requests:%d\n", finalErrors)
	fmt.Printf("Tatsächliche RPS:   %.2f\n", actualRPS)
	fmt.Println("--- Ende des Load Tests ---")
}

func worker(ctx context.Context, wg *sync.WaitGroup, client *http.Client, baseURL string, rpsPerWorker float64, workerID int) {
	defer wg.Done()

	var interval time.Duration
	if rpsPerWorker > 0 {
		// Berechne das Intervall zwischen Requests für diesen Worker
		// Umrechnung in Nanosekunden für time.Duration
		interval = time.Duration(1e9 / rpsPerWorker)
	} else {
		interval = 0 // Kein Delay, wenn RPS unbegrenzt oder 0 ist
	}

	// Ticker für Rate Limiting, falls Intervall > 0
	var ticker *time.Ticker
	if interval > 0 {
		ticker = time.NewTicker(interval)
		defer ticker.Stop()
	}

	baseURLClean := strings.TrimSuffix(baseURL, "/") // Stelle sicher, dass URL nicht mit / endet
	errorURL := baseURLClean + "/error"

	for {
		// Prüfe zuerst, ob die Zeit abgelaufen ist oder abgebrochen wurde
		select {
		case <-ctx.Done():
			return // Zeit ist um oder Kontext wurde abgebrochen
		default:
			// Kein Abbruch, fahre fort
		}

		// Rate Limiting: Warte auf den nächsten Tick (oder fahre sofort fort, wenn interval <= 0)
		if ticker != nil {
			select {
			case <-ctx.Done(): // Erneut prüfen, falls wir im Ticker warten
				return
			case <-ticker.C:
				// Zeit für den nächsten Request
			}
		}

		// Bestimme die Ziel-URL (Fehler jede 10. Anfrage)
		// Wichtig: Inkrementiere atomar und *hole* den neuen Wert für die Prüfung
		currentRequestNum := atomic.AddUint64(&requestCounter, 1)
		reqURL := baseURLClean
		if currentRequestNum%10 == 0 {
			reqURL = errorURL
		}

		// Erstelle den Request mit Kontext (wichtig für Timeout/Abbruch)
		req, err := http.NewRequestWithContext(ctx, "GET", reqURL, nil)
		if err != nil {
			// Sollte selten passieren, aber zählt als Fehler
			atomic.AddUint64(&errorCounter, 1)
			// Logge diesen Fehler evtl., da er ein Setup-Problem ist?
			// fmt.Fprintf(os.Stderr, "Worker %d: Fehler beim Erstellen des Requests: %v\n", workerID, err)
			continue // Nächste Iteration
		}

		// Führe den Request aus
		resp, err := client.Do(req)
		if err != nil {
			atomic.AddUint64(&errorCounter, 1)
			// Netzwerkfehler etc. - kein Log im normalen Betrieb
			// fmt.Fprintf(os.Stderr, "Worker %d: Fehler beim Senden des Requests an %s: %v\n", workerID, reqURL, err)
			// Wenn ein Response vorhanden ist (z.B. bei Timeout während Body Read), trotzdem Body schließen
			if resp != nil && resp.Body != nil {
				io.Copy(io.Discard, resp.Body) // Lese und verwerfe Body
				resp.Body.Close()
			}
			continue // Nächste Iteration
		}

		// WICHTIG: Response Body lesen und schließen, um Connection wiederzuverwenden!
		// io.Copy liest bis EOF oder Fehler und gibt die Anzahl Bytes zurück.
		// io.Discard ist ein Writer, der alles verwirft.
		_, _ = io.Copy(io.Discard, resp.Body)
		resp.Body.Close()

		// Prüfe den Status Code
		if resp.StatusCode >= 400 {
			atomic.AddUint64(&errorCounter, 1)
			// Kein Log im normalen Betrieb
		}

		// Kein explizites Sleep hier, der Ticker steuert die Rate
		// Wenn interval 0 ist (unlimitierte RPS), läuft die Schleife so schnell wie möglich
	}
}
