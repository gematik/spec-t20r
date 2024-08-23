# Policy Information Point und Policy Administration Point API

## Übersicht

Diese API ist Teil der gematik Zero Trust Telematikinfrastruktur und implementiert Download-Endpunkte für OPA-kompatible PIP- und PAP-Bundles. Open Policy Agents der Telematikinfrastruktur können Bundles (mit Richtlinien und/oder Daten) für ihre Anwendung abrufen. Die Bundles werden von der zentralen administrativen OPA-Instanz signiert.

## Version

**API-Version:** 1.0.0

## Server

- **Local Development Server:** `http://localhost:8080`
- **Reference Server:** `https://pip-pap-test.ti-dienste.de`
- **Reference Server:** `https://pip-pap-ref.ti-dienste.de`
- **Production Server:** `https://pip-pap.ti-dienste.de`

## Tags

- **PIP_and_PAP:** Policy Information Point and Policy Administration Point

## Endpunkte

### 1. Abrufen eines signierten OPA-Bundles

**Pfad:** `/policies/{application}/{label}`

#### Pfadparameter

- **application (string, erforderlich):** Name der Anwendung.
- **label (string, erforderlich):** Label des Richtlinien- und/oder Datenbundles. Beispiel: `latest`.

#### Header-Parameter

- **If-None-Match (string, optional):** Die Revision des zuletzt abgerufenen Bundles (ETag-Header).

#### Optionen (OPTIONS)

- **Beschreibung:** Abfrage der zulässigen HTTP-Methoden für diese Ressource.
- **Antworten:**
  - **200 OK**
    - **Headers:**
      - **Allow (string):** Zulässige HTTP-Methoden. Beispiel: `GET, HEAD, OPTIONS`.

#### Abrufen eines Bundles (GET)

- **Beschreibung:** Abrufen eines signierten OPA-Bundles für die angegebene Anwendung und das Label. Der Dienst vergleicht den Wert des If-None-Match-Headers mit der aktuellen Revision des Bundles. Wenn sich das Bundle seit dem letzten Update nicht geändert hat, antwortet der Server mit HTTP 304 Not Modified.

- **Antworten:**
  - **200 OK**
    - **Headers:**
      - **ETag (string):** Die Revision des Richtlinienbundles.
      - **Content-Disposition (string):** Beispiel: `attachment; filename=bundle.tar.gz`
    - **Content:**
      - **application/gzip (binary):** Das signierte OPA-Bundle.

  - **304 Not Modified**
    - **Beschreibung:** Das Bundle wurde seit dem letzten Abruf nicht geändert.

  - **400 Invalid bundle type**
    - **Content-Type:** `application/json`
    - **Beispiel:**
      ```json
      {
        "error": "Invalid bundle type."
      }
      ```

  - **404 Not Found**
    - **Content-Type:** `application/json`
    - **Beispiel:**
      ```json
      {
        "error": "The requested bundle does not exist."
      }
      ```

## Lizenz und Support

Für Fragen und Unterstützung wenden Sie sich bitte an das zuständige Team der gematik.

