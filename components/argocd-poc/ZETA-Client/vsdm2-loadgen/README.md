# vsdm2-loadgen.py

Ein einfaches Python Skript zum Generieren von Last auf einen VSD Service

**Erklärung des Skripts:**

1.  **Shebang:** `#!/usr/bin/env python3` - Definiert den Interpreter für das Skript (Python 3).
2.  **Docstring:** Der mehrzeilige String am Anfang des Skripts ist ein Docstring. Er dient als Dokumentation und wird von der `print_usage()` Funktion verwendet, um die Usage-Anzeige zu generieren.
3.  **Importe:**
    *   `argparse`:  Für die Verarbeitung von Kommandozeilenparametern.
    *   `time`: Für Zeitfunktionen wie `sleep()` zur Steuerung der Request-Rate und für die Messung der Dauer.
    *   `requests`:  Für das Senden von HTTP Requests.
    *   `sys`:  Für `sys.exit()` um das Skript mit unterschiedlichen Exit Codes zu beenden.
4.  **`print_usage()` Funktion:**
    *   Gibt den Docstring des Skripts aus. Dieser Docstring enthält die Usage-Anzeige.
5.  **`main()` Funktion:**
    *   **Argument Parser:**
        *   `argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS)`: Erstellt einen Argument Parser. `add_help=False` verhindert, dass `argparse` automatisch eine `-h` oder `--help` Option hinzufügt (wir wollen es selbst steuern). `usage=argparse.SUPPRESS` unterdrückt die automatische Usage-Anzeige bei Fehlern, damit wir unsere eigene anzeigen können.
        *   `parser.add_argument(...)`: Definiert die Kommandozeilenparameter:
            *   `--rps`:  Requests pro Sekunde (Integer, erforderlich).
            *   `--duration`: Dauer in Sekunden (Integer, erforderlich).
            *   `--url`: Ziel URL (String, optional, Standardwert ist `http://localhost/vsdservice/v1/vsdmbundle`).
            *   `--help`:  Hilfe Flag (Action `store_true`, speichert `True` wenn `--help` angegeben ist).
        *   `args = parser.parse_args()`: Parsed die Kommandozeilenargumente und speichert sie in der `args` Variable.
    *   **Usage Anzeige und Fehlerbehandlung:**
        *   `if args.help or not (args.rps and args.duration):`:  Prüft, ob `--help` angegeben wurde oder ob die Pflichtparameter (`--rps` und `--duration`) fehlen.
        *   `print_usage()`:  Gibt die Usage-Anzeige aus.
        *   `sys.exit(0 if args.help else 1)`: Beendet das Skript. Exit Code `0` wenn `--help` angegeben wurde (erfolgreiche Hilfeanzeige), Exit Code `1` wenn Pflichtparameter fehlen (Fehler).
        *   Prüft, ob `rps` und `duration` positive Werte sind. Wenn nicht, wird eine Fehlermeldung ausgegeben, die Usage-Anzeige gezeigt und das Skript mit Exit Code 1 beendet.
    *   **Ausgabe der Konfiguration:**
        *   Gibt die konfigurierte URL, RPS und Dauer auf der Konsole aus.
    *   **Rate Limiting und Request Schleife:**
        *   `sleep_interval = 1.0 / rps`: Berechnet das Intervall zwischen den Requests, um die gewünschte RPS zu erreichen.
        *   `start_time = time.time()`: Speichert die Startzeit des Tests.
        *   `request_count = 0`, `error_count = 0`:  Initialisiert Zähler für erfolgreiche und fehlerhafte Requests.
        *   **`try...except KeyboardInterrupt...finally` Block:**
            *   `try`:  Enthält die Hauptschleife des Load Tests.
            *   `for _ in range(duration):`:  Äußere Schleife, die für die angegebene Dauer läuft (in Sekunden).
            *   `end_time_for_second = start_time + 1`:  Berechnet die Zielzeit für das Ende der aktuellen Sekunde.
            *   `requests_this_second = 0`: Zähler für Requests in der aktuellen Sekunde.
            *   `while time.time() < end_time_for_second and requests_this_second < rps:`: Innere Schleife, die Requests sendet, bis entweder das Ende der Sekunde erreicht ist oder die gewünschte RPS für diese Sekunde erreicht wurde.
            *   `response = requests.get(url)`: Sendet einen HTTP GET Request an die Ziel URL.
            *   `response.raise_for_status()`: Prüft den HTTP Status Code der Antwort. Wenn es ein Fehlercode (4xx oder 5xx) ist, wird eine `requests.exceptions.HTTPError` Exception ausgelöst.
            *   `request_count += 1`: Erhöht den Zähler für erfolgreiche Requests.
            *   `requests_this_second += 1`: Erhöht den Zähler für Requests in der aktuellen Sekunde.
            *   `except requests.exceptions.RequestException as e:`: Fängt `requests.exceptions.RequestException` Exceptions ab, die bei Netzwerkproblemen oder HTTP Fehlern auftreten können. Gibt eine Fehlermeldung aus und erhöht den `error_count`.
            *   `time.sleep(sleep_interval)`:  Fügt eine Pause ein, um die Request-Rate zu steuern.
            *   `start_time += 1`:  Erhöht die `start_time` um 1 Sekunde für die nächste Iteration der äußeren Schleife.
            *   `except KeyboardInterrupt:`: Fängt `KeyboardInterrupt` Exceptions ab, die auftreten, wenn der Benutzer das Skript mit Strg+C abbricht. Gibt eine Abbruchmeldung aus.
            *   `finally:`:  Wird immer ausgeführt, egal ob Exceptions aufgetreten sind oder nicht. Hier wird die Zusammenfassung des Load Tests ausgegeben.
    *   **Zusammenfassung des Load Tests:**
        *   Berechnet die tatsächliche Dauer und RPS.
        *   Gibt eine Zusammenfassung mit Ziel-URL, geplanter RPS und Dauer, tatsächlicher Dauer, Anzahl der gesendeten und fehlerhaften Requests und der tatsächlichen RPS aus.
    *   `if __name__ == "__main__":`:  Stellt sicher, dass die `main()` Funktion nur ausgeführt wird, wenn das Skript direkt ausgeführt wird (nicht wenn es als Modul importiert wird).

**Wie man das Skript verwendet:**

1.  **Speichern:** Speichern Sie den Code als `vsdm2-loadgen.py` in einem Verzeichnis.
2.  **Ausführbar machen:**  Geben Sie dem Skript Ausführungsrechte: `chmod +x vsdm2-loadgen.py`
3.  **Ausführen:**
    *   **Mit Standard URL und 10 RPS für 60 Sekunden:**
        ```bash
        ./vsdm2-loadgen.py --rps 10 --duration 60
        ```
    *   **Mit benutzerdefinierter URL und 50 RPS für 300 Sekunden:**
        ```bash
        ./vsdm2-loadgen.py --rps 50 --duration 300 --url http://meinvsdservice.example.com/vsdservice/v1/vsdmbundle
        ```
    *   **Usage Anzeige:**
        ```bash
        ./vsdm2-loadgen.py --help
        ```
        Oder wenn Sie falsche Parameter angeben, z.B.:
        ```bash
        ./vsdm2-loadgen.py --rps 0 --duration -10
        ```

**Wichtige Hinweise:**

*   **Rate Limiting:** Das `time.sleep(sleep_interval)` sorgt für ein einfaches Rate Limiting. Die Genauigkeit des Rate Limitings hängt von der Genauigkeit von `time.sleep()` und der Systemlast ab. Für sehr hohe RPS könnte es sein, dass das Rate Limiting nicht perfekt genau ist.
*   **Fehlerbehandlung:** Das Skript behandelt `requests.exceptions.RequestException`, die eine breite Palette von Problemen abdeckt (Netzwerkfehler, Timeouts, HTTP Fehler usw.). Sie können die Fehlerbehandlung bei Bedarf weiter verfeinern.
*   **Anpassung:** Sie können das Skript leicht anpassen, um andere HTTP Methoden (z.B. POST, PUT) oder Request-Payloads zu verwenden, falls Ihr VSD Service dies erfordert. Sie können auch weitere Kommandozeilenparameter hinzufügen, z.B. für Header, Timeouts usw.
*   **Last des Zielsystems:**  Seien Sie vorsichtig, wenn Sie hohe RPS-Werte verwenden, da dies Ihr Zielsystem überlasten kann. Beginnen Sie mit niedrigen Werten und erhöhen Sie diese schrittweise, um die Auswirkungen auf Ihr System zu beobachten.