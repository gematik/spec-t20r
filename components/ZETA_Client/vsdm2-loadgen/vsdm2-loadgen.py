#!/usr/bin/env python3

"""
vsdm2-loadgen.py

Erzeugt Last auf einen VSD Service Endpoint, indem es HTTP GET Requests sendet.
Unterstützt parallele Requests mit Threads.

Verwendung:
  vsdm2-loadgen.py --rps <requests_per_second> --duration <duration_in_seconds> [--url <ziel_url>] [--log-level <level>] [--threads <num_threads>]

Optionen:
  --rps <requests_per_second>   Gesamtzahl der Requests pro Sekunde, die gesendet werden sollen (verteilt über Threads).
  --duration <duration_in_seconds> Dauer des Lasttests in Sekunden.
  --url <ziel_url>              URL des VSD Service Endpoints (optional, Standard: http://localhost/vsdservice/v1/vsdmbundle).
  --log-level <level>           Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Standard: INFO.
  --threads <num_threads>       Anzahl der parallelen Threads für Requests. Standard: 1.
  --help                        Zeigt diese Hilfemeldung an.

Beispiele:
  vsdm2-loadgen.py --rps 100 --duration 60
  vsdm2-loadgen.py --rps 1000 --duration 300 --url http://meinvsdservice.example.com/vsdservice/v1/vsdmbundle --log-level DEBUG --threads 10
"""

import argparse
import time
import requests
import sys
import tqdm
import coloredlogs
import logging
import threading

def print_usage():
    """Gibt die Usage-Anzeige aus."""
    print(__doc__)

request_count_global = 0
error_count_global = 0

def send_requests_thread(url, duration, rps_thread, log_level_str, thread_id):
    """Funktion, die von jedem Thread ausgeführt wird, um Requests zu senden."""
    global request_count_global, error_count_global
    sleep_interval_thread = 1.0 / rps_thread if rps_thread > 0 else 0
    start_time_thread = time.time()
    logger_thread = logging.getLogger(f"{__name__}.thread-{thread_id}") # Logger für jeden Thread

    logger_thread.debug(f"Thread-{thread_id}: Starte, RPS pro Thread: {rps_thread}, Sleep Interval: {sleep_interval_thread:.4f}")

    start_time_second = time.time()

    for second in range(duration):
        end_time_for_second = start_time_second + 1
        requests_this_second = 0
        while time.time() < end_time_for_second and requests_this_second < rps_thread:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with threading.Lock(): # Thread-safe increment für globale Zähler
                    global request_count_global
                    request_count_global += 1
                requests_this_second += 1
                logger_thread.debug(f"Thread-{thread_id}: Request erfolgreich gesendet. Status Code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger_thread.error(f"Thread-{thread_id}: Fehler beim Senden des Requests: {e}")
                logger_thread.debug(f"Thread-{thread_id}: Exception details: {e}")
                with threading.Lock(): # Thread-safe increment für globale Fehlerzähler
                    global error_count_global
                    error_count_global += 1
            time.sleep(sleep_interval_thread)
        start_time_second += 1 # Startzeit für nächste Sekunde setzen

    logger_thread.debug(f"Thread-{thread_id}: Beendet.")


def main():
    """Hauptfunktion des Load Generators."""
    global request_count_global, error_count_global
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS) # Unterdrücke Standard-Help, wir machen es selbst
    parser.add_argument('--rps', type=int, default=20, help='Requests pro Sekunde')
    parser.add_argument('--duration', type=int, default=10, help='Dauer in Sekunden')
    parser.add_argument('--url', type=str, default='http://localhost/vsdservice/v1/vsdmbundle', help='Ziel URL (optional)')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Logging Level (optional)')
    parser.add_argument('--threads', type=int, default=1, help='Anzahl paralleler Threads (optional)')
    parser.add_argument('--help', action='store_true', help='Hilfe anzeigen')

    args = parser.parse_args()

    if args.help or not (args.rps and args.duration): # Zeige Usage bei --help oder fehlenden Pflichtparametern
        print_usage()
        sys.exit(0 if args.help else 1) # Exit Code 0 bei --help, 1 bei Fehler

    rps = args.rps
    duration = args.duration
    url = args.url
    log_level_str = args.log_level.upper()
    num_threads = args.threads

    # Configure logging with coloredlogs
    logging.basicConfig(level=logging.INFO) # Basic config needed for coloredlogs to work
    field_styles = coloredlogs.DEFAULT_FIELD_STYLES
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES
    if log_level_str == 'DEBUG':
        level_styles['debug'] = {'color': 'cyan'} # Make debug level more visible
    coloredlogs.install(level=log_level_str, field_styles=field_styles, level_styles=level_styles)
    logger = logging.getLogger(__name__) # Get logger for main module

    if rps <= 0 or duration <= 0 or num_threads <= 0:
        logger.error("RPS, Duration und Threads müssen positive Werte sein.")
        print_usage()
        sys.exit(1)

    logger.info(f"Starte Load Test gegen URL: {url}")
    logger.info(f"  Gesamt Requests pro Sekunde (RPS): {rps}")
    logger.info(f"  Dauer: {duration} Sekunden")
    logger.info(f"  Anzahl Threads: {num_threads}")
    logger.debug(f"Logging Level gesetzt auf: {log_level_str}")

    start_time_global = time.time()
    request_count_global = 0 # Zurücksetzen der globalen Zähler
    error_count_global = 0

    threads = []
    rps_thread = rps / num_threads # RPS pro Thread berechnen

    try:
        for i in range(num_threads):
            thread = threading.Thread(target=send_requests_thread, args=(url, duration, rps_thread, log_level_str, i+1))
            threads.append(thread)
            thread.start()

        with tqdm.tqdm(total=duration, desc="Fortschritt", unit="Sekunde", dynamic_ncols=True) as pbar:
            while True:
                if all(not t.is_alive() for t in threads): # Überprüfen, ob alle Threads beendet sind
                    break
                time.sleep(1) # Warte 1 Sekunde
                pbar.update(1) # Progressbar pro Sekunde aktualisieren

    except KeyboardInterrupt:
        print("\nLoad Test abgebrochen durch Benutzer.")
        logger.warning("Load Test manuell abgebrochen.")

    finally:
        for thread in threads: # Sicherstellen, dass alle Threads beendet sind (sollten es bereits sein)
            thread.join()

        elapsed_time = time.time() - start_time_global
        actual_rps = request_count_global / elapsed_time if elapsed_time > 0 else 0
        print("\n--- Load Test Zusammenfassung ---")
        print(f"Ziel URL: {url}")
        print(f"Geplante Gesamt RPS: {rps}")
        print(f"Geplante Dauer: {duration} Sekunden")
        print(f"Anzahl Threads: {num_threads}")
        print(f"Tatsächliche Dauer: {elapsed_time:.2f} Sekunden")
        print(f"Gesendete Requests: {request_count_global}")
        print(f"Fehlerhafte Requests: {error_count_global}")
        print(f"Tatsächliche RPS (ungefähr): {actual_rps:.2f}")
        print("--- Ende des Load Tests ---")
        logger.info("Load Test abgeschlossen.")

if __name__ == "__main__":
    main()