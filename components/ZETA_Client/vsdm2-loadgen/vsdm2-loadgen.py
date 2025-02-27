#!/usr/bin/env python3

"""
vsdm2-loadgen.py

Erzeugt Last auf einen VSD Service Endpoint, indem es HTTP GET Requests sendet.

Verwendung:
  vsdm2-loadgen.py --rps <requests_per_second> --duration <duration_in_seconds> [--url <ziel_url>] [--log-level <level>]

Optionen:
  --rps <requests_per_second>   Anzahl der Requests pro Sekunde, die gesendet werden sollen.
  --duration <duration_in_seconds> Dauer des Lasttests in Sekunden.
  --url <ziel_url>              URL des VSD Service Endpoints (optional, Standard: http://localhost/vsdservice/v1/vsdmbundle).
  --log-level <level>           Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Standard: INFO.
  --help                        Zeigt diese Hilfemeldung an.

Beispiele:
  vsdm2-loadgen.py --rps 10 --duration 60
  vsdm2-loadgen.py --rps 50 --duration 300 --url http://meinvsdservice.example.com/vsdservice/v1/vsdmbundle --log-level DEBUG
"""

import argparse
import time
import requests
import sys
import tqdm
import coloredlogs
import logging

def print_usage():
    """Gibt die Usage-Anzeige aus."""
    print(__doc__)

def main():
    """Hauptfunktion des Load Generators."""
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS) # Unterdrücke Standard-Help, wir machen es selbst
    parser.add_argument('--rps', type=int, default=20, help='Requests pro Sekunde')
    parser.add_argument('--duration', type=int, default=10, help='Dauer in Sekunden')
    parser.add_argument('--url', type=str, default='http://localhost/vsdservice/v1/vsdmbundle', help='Ziel URL (optional)')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Logging Level (optional)')
    parser.add_argument('--help', action='store_true', help='Hilfe anzeigen')

    args = parser.parse_args()

    if args.help or not (args.rps and args.duration): # Zeige Usage bei --help oder fehlenden Pflichtparametern
        print_usage()
        sys.exit(0 if args.help else 1) # Exit Code 0 bei --help, 1 bei Fehler

    rps = args.rps
    duration = args.duration
    url = args.url
    log_level_str = args.log_level.upper()

    # Configure logging with coloredlogs
    logging.basicConfig(level=logging.INFO) # Basic config needed for coloredlogs to work
    field_styles = coloredlogs.DEFAULT_FIELD_STYLES
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES
    if log_level_str == 'DEBUG':
        level_styles['debug'] = {'color': 'cyan'} # Make debug level more visible
    coloredlogs.install(level=log_level_str, field_styles=field_styles, level_styles=level_styles)
    logger = logging.getLogger(__name__) # Get logger for this module

    if rps <= 0 or duration <= 0:
        logger.error("RPS und Duration müssen positive Werte sein.")
        print_usage()
        sys.exit(1)

    logger.info(f"Starte Load Test gegen URL: {url}")
    logger.info(f"  Requests pro Sekunde (RPS): {rps}")
    logger.info(f"  Dauer: {duration} Sekunden")
    logger.debug(f"Logging Level gesetzt auf: {log_level_str}")

    sleep_interval = 1.0 / rps
    start_time = time.time()
    request_count = 0
    error_count = 0

    try:
        for second in tqdm.tqdm(range(duration), desc="Fortschritt", unit="Sekunde", dynamic_ncols=True):
            end_time_for_second = start_time + 1  # Zielzeit für das Ende der aktuellen Sekunde
            requests_this_second = 0
            while time.time() < end_time_for_second and requests_this_second < rps:
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Wirf einen Fehler für HTTP Fehlercodes (4xx oder 5xx)
                    request_count += 1
                    requests_this_second += 1
                    logger.debug(f"Request erfolgreich gesendet. Status Code: {response.status_code}") # Optional: Erfolgsmeldung ausgeben
                except requests.exceptions.RequestException as e:
                    logger.error(f"Fehler beim Senden des Requests: {e}")
                    logger.debug(f"Exception details: {e}")
                    error_count += 1
                time.sleep(sleep_interval) # Rate Limiting
            start_time += 1 # Starte die nächste Sekunde beim nächsten Durchlauf

    except KeyboardInterrupt:
        print("\nLoad Test abgebrochen durch Benutzer.")
        logger.warning("Load Test manuell abgebrochen.")

    finally:
        elapsed_time = time.time() - start_time
        actual_rps = request_count / elapsed_time if elapsed_time > 0 else 0
        print("\n--- Load Test Zusammenfassung ---")
        print(f"Ziel URL: {url}")
        print(f"Geplante RPS: {rps}")
        print(f"Geplante Dauer: {duration} Sekunden")
        print(f"Tatsächliche Dauer: {elapsed_time:.2f} Sekunden")
        print(f"Gesendete Requests: {request_count}")
        print(f"Fehlerhafte Requests: {error_count}")
        print(f"Tatsächliche RPS (ungefähr): {actual_rps:.2f}")
        print("--- Ende des Load Tests ---")
        logger.info("Load Test abgeschlossen.")

if __name__ == "__main__":
    main()