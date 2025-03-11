import argparse
import asyncio
import aiohttp
import time
import sys
import tqdm
import logging
import coloredlogs
from collections import deque

async def send_request(session, url, thread_id, request_counter, error_count):
    """Sendet eine einzelne HTTP GET-Anfrage asynchron."""
    target_url = url if request_counter % 10 != 0 else url.rstrip('/') + "/error"  # Fehler alle 10 Requests
    try:
        async with session.get(target_url) as response:
            await response.text() # Liest den Response Body, wichtig für keep-alive
            if response.status >= 400: # Explizites Logging für Fehlerhafte Responses - ENTFERNT
                # logging.warning(f"Thread-{thread_id}: Request an {target_url} erhielt Status: {response.status}") # ENTFERNT
                error_count.append(1)
                return False
            logging.debug(f"Thread-{thread_id}: Request an {target_url} erfolgreich. Status: {response.status}")
            return True
    except Exception as e:
        logging.error(f"Thread-{thread_id}: Fehler beim Senden des Requests an {target_url}: {e}")
        error_count.append(1)
        return False

async def worker(url, rps, duration, thread_id, results, error_count, progress_queue):
    """Worker-Funktion für das Senden von Requests."""
    interval = 1.0 / rps if rps > 0 else 0
    request_counter = 0
    success_count = 0  # Zähler für erfolgreiche Requests in diesem Worker
    batch_size = 100 # Größe des Batches für Fortschrittsaktualisierung
    async with aiohttp.ClientSession() as session: # Session pro Worker für Connection-Reuse
        start_time = time.time()
        while time.time() - start_time < duration: # Zeitbasierte Schleife für genauere Dauer
            request_counter += 1
            success = await send_request(session, url, thread_id, request_counter, error_count)
            if success:
                success_count += 1
            if request_counter % batch_size == 0: # Fortschritt nur alle batch_size Requests melden
                progress_queue.append(batch_size) # Batchgröße statt 1 übergeben
            if interval > 0: # Rate Limiting nur wenn rps > 0
                await asyncio.sleep(interval)
        # Restliche erfolgreiche Requests am Ende des Workers hinzufügen
        if success_count % batch_size != 0:
             progress_queue.append(success_count % batch_size)

async def progress_updater(total_requests, progress_queue, workers_done, rps_values):
    """Aktualisiert die Fortschrittsanzeige asynchron und mittelt RPS."""
    completed_requests = 0
    last_rps_value = 0 # Zwischenspeicher für den letzten RPS Wert
    with tqdm.tqdm(total=total_requests, desc="Fortschritt", unit="Requests", dynamic_ncols=True, initial=0) as pbar:
        try:
            while completed_requests < total_requests or not workers_done.is_set(): # Überprüfe completed_requests statt Queue-Länge
                batch_update = 0
                while progress_queue: # Queue leeren und Batch-Updates summieren
                    batch_update += progress_queue.popleft()
                completed_requests += batch_update
                pbar.update(batch_update) # Batch-Update verwenden
                current_rps_str = pbar.format_dict['rate'] # Zugriff auf aktuelle RPS als String
                if current_rps_str and current_rps_str != '?': #  Sicherstellen, dass Wert vorhanden und keine '?'
                    try:
                        current_rps = float(current_rps_str) # Umwandeln in float
                        if current_rps > 0: # Ungültige oder Nullwerte ausschließen
                            rps_values.append(current_rps) # Hinzufügen zur Liste
                            last_rps_value = current_rps # Speichern für den Fall, dass Schleife abbricht bevor ein neuer Wert kommt
                    except ValueError:
                        logging.warning(f"Konnte RPS Wert nicht parsen: {current_rps_str}") # Logging für Parse Fehler
                await asyncio.sleep(0.1) # Weniger häufig updaten
        except asyncio.CancelledError:
            pass
        finally:
            if not rps_values and last_rps_value > 0: # Fallback, falls keine Werte gesammelt wurden aber ein letzter Wert existiert
                rps_values.append(last_rps_value) # Letzten Wert verwenden, um Division durch Null zu verhindern

async def main():
    """Hauptfunktion für den asynchronen Load Generator."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--rps', type=int, default=1000, help='Requests pro Sekunde')
    parser.add_argument('--duration', type=int, default=10, help='Dauer in Sekunden')
    parser.add_argument('--url', type=str, default='http://localhost/vsdservice/v1/vsdmbundle', help='Ziel URL')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Logging Level')
    parser.add_argument('--threads', type=int, default=10, help='Anzahl paralleler Tasks')
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper())
    coloredlogs.install(level=args.log_level.upper())

    total_requests = args.rps * args.duration
    results = [] # Nicht mehr benötigt für Performance-Optimierung
    error_count = []
    tasks = []
    progress_queue = deque()
    workers_done = asyncio.Event()
    rps_values = [] # Liste zum Speichern der RPS-Werte

    # RPS gleichmäßig auf Threads verteilen, aber mindestens 1 RPS pro Thread
    thread_rps = max(1, args.rps / args.threads)

    for i in range(args.threads):
        tasks.append(worker(args.url, thread_rps, args.duration, i, results, error_count, progress_queue))

    progress_task = asyncio.create_task(progress_updater(total_requests, progress_queue, workers_done, rps_values))

    start_time = time.time()
    await asyncio.gather(*tasks)
    workers_done.set()
    progress_task.cancel()
    try:
        await progress_task
    except asyncio.CancelledError:
        pass
    elapsed_time = time.time() - start_time

    sent_requests = 0
    for task in tasks: # Anzahl gesendeter Requests zählen, ist genauer als len(results)
        sent_requests_worker = int(thread_rps * args.duration) # Sollte ungefähr der Plan entsprechen
        sent_requests += sent_requests_worker

    average_rps = sum(rps_values) / len(rps_values) if rps_values else 0 # Durchschnittliche RPS berechnen

    print("\n--- Load Test Zusammenfassung ---")
    print(f"Ziel URL: {args.url}")
    print(f"Geplante Gesamt RPS: {args.rps}")
    print(f"Geplante Dauer: {args.duration} Sekunden")
    print(f"Anzahl Threads: {args.threads}")
    print(f"Tatsächliche Dauer: {elapsed_time:.2f} Sekunden")
    print(f"Gesendete Requests (ungefähr): {sent_requests}") # Angepasste Ausgabe
    print(f"Fehlerhafte Requests: {len(error_count)}")
    print(f"Tatsächliche RPS (ungefähr): {average_rps:.2f}") # Angepasste RPS Berechnung, Durchschnittswert
    print("--- Ende des Load Tests ---")
    logging.info("Load Test abgeschlossen.")

if __name__ == "__main__":
    asyncio.run(main())