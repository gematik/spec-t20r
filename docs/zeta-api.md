# ZETA API

![gematik logo](/images/gematik_logo.svg)

Eine gute API-Dokumentation sollte umfassend und klar strukturiert sein, um Entwicklern die Nutzung der API so einfach wie möglich zu machen. Hier sind die wichtigsten Elemente, die eine gute API-Dokumentation enthalten sollte:

## 1.1. Einführung

Zweck der API: Eine kurze Erklärung, was die API tut und welche Probleme sie löst.
Zielgruppe: Wer sollte diese API nutzen? Welche technischen Vorkenntnisse werden erwartet?
Voraussetzungen: Informationen über benötigte Tools, Bibliotheken oder SDKs.

## 1.2. Inhalt

- [ZETA API](#zeta-api)
  - [1.1. Einführung](#11-einführung)
  - [1.2. Inhalt](#12-inhalt)
  - [1.3 Voraussetzungen für die ZETA Client Nutzung](#13-voraussetzungen-für-die-zeta-client-nutzung)
    - [1.3.1 VSDM2](#131-vsdm2)
  - [1.4 Ablauf](#14-ablauf)
    - [1.4.1 Konfiguration und Discovery](#141-konfiguration-und-discovery)
    - [1.4.2 Client-Registrierung](#142-client-registrierung)
      - [1.4.2.1 Stationäre Clients](#1421-stationäre-clients)
      - [1.4.2.2 Mobile Clients](#1422-mobile-clients)
    - [1.4.3 Authentifizierung und Autorisierung](#143-authentifizierung-und-autorisierung)
  - [1.5. Endpunkte](#15-endpunkte)
    - [1.5.1 ZETA Guard API Endpunkte](#151-zeta-guard-api-endpunkte)
      - [1.5.1.1 OAuth Protected Resource Well-Known Endpoint](#1511-oauth-protected-resource-well-known-endpoint)
        - [1.5.1.1.1 Basis-URL](#15111-basis-url)
        - [1.5.1.1.2 Anfragen](#15112-anfragen)
        - [1.5.1.2.3 Antworten](#15123-antworten)
      - [1.5.1.2 Authorization Server Well-Known Endpoint](#1512-authorization-server-well-known-endpoint)
        - [1.5.1.2.1 Basis-URL](#15121-basis-url)
        - [1.5.1.2.2 Anfragen](#15122-anfragen)
        - [1.5.1.2.3 Antworten](#15123-antworten-1)
      - [1.5.1.3 Nonce Endpoint](#1513-nonce-endpoint)
        - [1.5.1.3.1 Basis-URL](#15131-basis-url)
        - [1.5.1.3.2 Anfragen](#15132-anfragen)
        - [1.5.1.3.3 Antworten](#15133-antworten)
      - [1.5.1.4 Dynamic Client Registration Endpoint](#1514-dynamic-client-registration-endpoint)
        - [1.5.1.4.1 Basis-URL](#15141-basis-url)
        - [1.5.1.4.2 Anfragen](#15142-anfragen)
        - [1.5.1.4.3 Antworten](#15143-antworten)
      - [1.5.1.5 Token Endpoint](#1515-token-endpoint)
        - [1.5.1.5.1 Basis-URL](#15151-basis-url)
        - [1.5.1.5.2 Anfragen](#15152-anfragen)
        - [1.5.1.5.3 Antworten](#15153-antworten)
      - [1.5.1.6 Resource Endpoint](#1516-resource-endpoint)
        - [1.5.1.6.1 Basis-URL](#15161-basis-url)
        - [1.5.1.6.2 Anfragen](#15162-anfragen)
        - [1.5.1.6.3 Antworten](#15163-antworten)
    - [1.5.2 Konnektor/TI-Gateway Endpunkte](#152-konnektorti-gateway-endpunkte)
      - [1.5.2.1 getCertificate](#1521-getcertificate)
      - [1.5.2.1 externalAuthenticate](#1521-externalauthenticate)
    - [1.5.3 ZETA Attestation Service Endpunkte](#153-zeta-attestation-service-endpunkte)
      - [1.5.3.1 getAttestation](#1531-getattestation)
  - [1.6. Versionierung](#16-versionierung)
  - [1.7. Performance- und Lastannahmen](#17-performance--und-lastannahmen)
        - [1.8 Rate Limits und Einschränkungen](#18-rate-limits-und-einschränkungen)
  - [1.9. Support und Kontaktinformationen](#19-support-und-kontaktinformationen)
  - [1.10. FAQs und Troubleshooting](#110-faqs-und-troubleshooting)
  - [1.11. Interaktive Dokumentation (optional)](#111-interaktive-dokumentation-optional)
  - [1.12. Changelog](#112-changelog)
  - [1.13. git Branch Modell](#113-git-branch-modell)
  - [1.14. Lizenzbedingungen](#114-lizenzbedingungen)

## 1.3 Voraussetzungen für die ZETA Client Nutzung

Der **FQDN des Resource Servers** wird vom ZETA Client benötigt, um die ZETA Guard API zu erreichen.

Die **roots.json Datei** wird vom ZETA Client benötigt, um die Trust Chain zu validieren. Diese Datei muss regelmäßig aktualisiert werden.

Zusätzlich gibt es anwendungsspezifische Voraussetzungen, die für die Nutzung der ZETA Guard API erforderlich sind.

### 1.3.1 VSDM2

Für VSDM2 Requests wird ein PoPP (Proof of Patient Presence) Token benötigt. Das PoPP Token muss im **Header PoPP** an den ZETA Client übergeben werden.

## 1.4 Ablauf

Die ZETA API ermöglicht es ZETA Clients, auf geschützte Ressourcen zuzugreifen und dabei Sicherheits- und Authentifizierungsmechanismen zu nutzen. Abhängig vom Zustand des ZETA Clients müssen verschiedene Teilabläufe ausgeführt werden, oder können übersprungen werden.
Die ZETA API besteht aus mehreren Endpunkten, die verschiedene Funktionen bereitstellen. Diese Endpunkte sind in verschiedene Kategorien unterteilt, um die Nutzung zu erleichtern. Die wichtigsten Abläufe sind:

- Konfiguration und Discovery: Der ZETA Client muss die Konfiguration der ZETA Guard API kennen, um die Endpunkte zu erreichen.
- Client-Registrierung: Der ZETA Client muss sich bei der ZETA Guard API registrieren, um Zugriff auf geschützte Ressourcen zu erhalten.
- Authentifizierung und Autorisierung: Der Nutzer muss sich authentifizieren, um auf geschützte Ressourcen zuzugreifen.

Die ZETA API ist so konzipiert, dass sie eine sichere und flexible Interaktion zwischen ZETA Clients und geschützten Ressourcen ermöglicht. Die folgenden Abschnitte beschreiben die einzelnen Abläufe im Detail.

---

### 1.4.1 Konfiguration und Discovery

### 1.4.2 Client-Registrierung

Der ZETA Client benötigt eine Client Registrierung an jedem ZETA Guard, über den auf geschützte Ressourcen zugegriffen werden soll. Die Registrierung erfolgt über den Dynamic Client Registration Endpoint der ZETA Guard API.

Für die Registrierung wird eine Client Identität benötigt (Client Instance Key Pair), die vom ZETA Client generiert wird. Diese Identität wird verwendet, um den ZETA Client bei der ZETA Guard API zu identifizieren und zu authentifizieren.
Die Registrierung erfolgt einmalig.

#### 1.4.2.1 Stationäre Clients

Die Registrierung erfolgt über den Dynamic Client Registration Endpoint der ZETA Guard API. Der ZETA Client sendet eine Anfrage an diesen Endpunkt, um sich zu registrieren. Die Anfrage enthält:

- Client Metadaten (Client Name, Client Instance Public Key)
- Eine nonce, die vom ZETA Guard generiert wird
- Client Attestation Informationen, die den ZETA Client identifizieren
- Eine Signatur der Anfrage, die mit dem Client Instance Private Key erstellt wurde
- Zusätzliche Informationen wie Redirect URIs, etc.

Die ZETA Guard API prüft die Anfrage und registriert den ZETA Client. Nach erfolgreicher Registrierung erhält der ZETA Client eine Client ID, die für die Authentifizierung bei der ZETA Guard API verwendet wird.

#### 1.4.2.2 Mobile Clients

Die Registrierung für mobile Clients erfolgt ähnlich wie bei stationären Clients.

### 1.4.3 Authentifizierung und Autorisierung

Wie können Nutzer sich authentifizieren und welche Berechtigungen gibt es?
Welche Sicherheitsmaßnahmen sind getroffen?

API-Schlüssel oder Token: Wie erhält der Nutzer einen API-Schlüssel oder ein Authentifizierungstoken?
Autorisierungsverfahren: Beschreibung der verwendeten Authentifizierungsmethoden (z.B. OAuth, Basic Auth).
Beispiele: Beispielanfragen für die Authentifizierung.

## 1.5. Endpunkte

### 1.5.1 ZETA Guard API Endpunkte

Basis-URL: Die grundlegende URL, von der alle API-Aufrufe ausgehen.
Endpunkte: Detaillierte Beschreibung aller verfügbaren Endpunkte, einschließlich:
HTTP-Methode: GET, POST, PUT, DELETE, etc.
Pfadparameter: Parameter, die in der URL enthalten sind.
Query-Parameter: Parameter, die in der URL als Abfrage angehängt werden.
Body-Parameter: Parameter, die im Body einer Anfrage gesendet werden.
Mögliche Antwortformate (JSON, XML)

Hier ist die API-Beschreibung für den OAuth Protected Resource Well-Known Endpoint, basierend auf den bereitgestellten RFCs und der YAML-Definition, strukturiert nach Ihren Vorgaben.

---

#### 1.5.1.1 OAuth Protected Resource Well-Known Endpoint

Dieser Endpunkt bietet eine standardisierte Methode für OAuth Protected Resources (OPR), um ihre Fähigkeiten und Konfigurationsdetails zu veröffentlichen. Er ermöglicht es Clients und anderen Entitäten, die notwendigen Informationen über die OPR abzurufen, wie z.B. unterstützte Schemata, Verifizierungsmethoden, Token-Introspektion-Endpunkte und unterstützte Scopes. Der Endpunkt ist unter dem Pfad `/.well-known/oauth-protected-resource` relativ zur Basis-URL der Protected Resource erreichbar.

---

##### 1.5.1.1.1 Basis-URL

Die Basis-URL für den OAuth Protected Resource Well-Known Endpoint ist die Origin (Schema, Host und optionaler Port) der Protected Resource selbst. Der feste Pfad `/.well-known/oauth-protected-resource` wird an diese Basis-URL angehängt.

**Format der URL:**
`<Basis-URL der Protected Resource>/.well-known/oauth-protected-resource`

**Beispiel:**
Wenn die Protected Resource unter `https://api.example.com` gehostet wird, wäre die vollständige URL des Endpunkts:
`https://api.example.com/.well-known/oauth-protected-resource`

---

##### 1.5.1.1.2 Anfragen

Der Endpunkt wird über eine einfache HTTP GET-Anfrage ohne Body oder spezielle Header (außer ggf. `Accept: application/json`) aufgerufen.

**Codebeispiele:**

**Curl:**

```bash
curl -X GET "https://api.example.com/.well-known/oauth-protected-resource" \
     -H "Accept: application/json"
```

---

##### 1.5.1.2.3 Antworten

Wie im obigen Abschnitt dargestellt, ist die typische erfolgreiche API-Antwort ein JSON-Objekt, das der im `opr-well-known.yaml`-Schema definierten Struktur entspricht. Der `Content-Type`-Header der Antwort ist `application/json`.

**Statuscodes:**

- **200 OK:**
  - **Bedeutung:** Die Anfrage war erfolgreich, und die Konfigurationsdaten der Protected Resource wurden als JSON-Objekt im Antwort-Body zurückgegeben.
  Eine erfolgreiche Anfrage liefert ein JSON-Objekt, das die Konfiguration der Protected Resource beschreibt. Die genauen Felder hängen von der Implementierung und den unterstützten Fähigkeiten der geschützten Resource ab.
  - **Beispielantwort:**

Content-Type: application/json

```json
{
  "resource": "https://api.example.com",
  "authorization_servers": [
    "https://auth1.example.com",
    "https://auth2.example.com"
  ],
  "jwks_uri": "https://api.example.com/.well-known/jwks.json",
  "scopes_supported": [
    "read",
    "write",
    "delete"
  ],
  "bearer_methods_supported": [
    "header",
    "body"
  ],
  "resource_signing_alg_values_supported": [
    "RS256",
    "ES256"
  ],
  "resource_name": "Example Protected API",
  "resource_documentation": "https://docs.example.com/api",
  "resource_policy_uri": "https://www.example.com/privacy",
  "resource_tos_uri": "https://www.example.com/terms",
  "tls_client_certificate_bound_access_tokens": true,
  "authorization_details_types_supported": [
    "payment_initiation",
    "account_access"
  ],
  "dpop_signing_alg_values_supported": [
    "ES256",
    "RS512"
  ],
  "dpop_bound_access_tokens_required": false,
  "signed_metadata": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNvdXJjZSI6Imh0dHBzOi8vYXBpLmV4YW1wbGUuY29tIn0.XYZ123abc456def789",
  "zeta_asl_use": "required"
}
```



- **404 Not Found:**
  - **Bedeutung:** Der angeforderte Well-Known Endpoint konnte auf dem Server nicht gefunden werden. Dies kann daran liegen, dass die Protected Resource diesen Endpunkt nicht hostet oder falsch konfiguriert ist.
  - **Beispielantwort:**

Content-Type: application/problem+json

```json
{
  "type": "https://example.com/probs/not-found",
  "title": "OAuth Protected Resource Configuration Not Found",
  "status": 404,
  "detail": "The requested OAuth Protected Resource Well-Known configuration could not be found at this path. Please verify the  base URL.",
  "instance": "/.well-known/oauth-protected-resource"
}
```

- **500 Internal Server Error:**
  - **Bedeutung:** Ein unerwarteter Fehler ist auf dem Server der Protected Resource aufgetreten, der die Verarbeitung der Anfrage verhindert hat.
  - **Beispielantwort:** Ein leerer Body, ein generischer 
Content-Type: application/problem+json

```json
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected internal error occurred while processing your request. Please try again later or contact support.",
  "instance": "/.well-known/oauth-protected-resource",
  "error_id": "c1f7a9d3e8b2f1c5a7d6e4b0c9f8a1b2" // Optionale anwendungsspezifische Erweiterung
}
```

---

#### 1.5.1.2 Authorization Server Well-Known Endpoint

##### 1.5.1.2.1 Basis-URL

##### 1.5.1.2.2 Anfragen

##### 1.5.1.2.3 Antworten

#### 1.5.1.3 Nonce Endpoint

##### 1.5.1.3.1 Basis-URL

##### 1.5.1.3.2 Anfragen

##### 1.5.1.3.3 Antworten

#### 1.5.1.4 Dynamic Client Registration Endpoint

##### 1.5.1.4.1 Basis-URL

##### 1.5.1.4.2 Anfragen

##### 1.5.1.4.3 Antworten

#### 1.5.1.5 Token Endpoint

##### 1.5.1.5.1 Basis-URL

##### 1.5.1.5.2 Anfragen

##### 1.5.1.5.3 Antworten

#### 1.5.1.6 Resource Endpoint

##### 1.5.1.6.1 Basis-URL

##### 1.5.1.6.2 Anfragen

##### 1.5.1.6.3 Antworten

### 1.5.2 Konnektor/TI-Gateway Endpunkte

#### 1.5.2.1 getCertificate

#### 1.5.2.1 externalAuthenticate

### 1.5.3 ZETA Attestation Service Endpunkte

#### 1.5.3.1 getAttestation

## 1.6. Versionierung

API-Versionierung: Hinweise darauf, wie Versionen der API verwaltet werden und wie Benutzer zwischen verschiedenen Versionen wechseln können.
Änderungsprotokoll: Ein Changelog, das alle wichtigen Änderungen und Updates dokumentiert.

## 1.7. Performance- und Lastannahmen

Leistungsanforderungen: Informationen über die erwartete Leistung der API, wie z.B. Antwortzeiten und Verfügbarkeit.
Lastannahmen: Informationen über das erwartete Lastverhalten auf der API, wie z.B. die Anzahl der gleichzeitigen Benutzer oder Anfragen pro Sekunde.

- SM(C)-B Signaturerstellung
- TPM Attestation
- ZETA Guard Clientregistrierung
- ZETA Guard Authentifizierung
- ZETA Guard PEP
- ZETA Guard Refresh Token Exchange

##### 1.8 Rate Limits und Einschränkungen

Der OAuth Protected Resource Well-Known Endpoint ist so konfiguriert, dass er eine Rate-Limiting-Strategie implementiert. Der ZETA Client muss die Rate Limits beachten, um eine Überlastung des Endpunkts zu vermeiden. Die genauen Limits können je nach Implementierung variieren, aber typischerweise gelten folgende Richtlinien:

- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset

oder:

- RateLimit-Policy
- RateLimit

**Beispiele**

[Draft RFC für Rate Limits](https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-09.html#name-ratelimit-policy-field)


## 1.9. Support und Kontaktinformationen

Hilfe: Informationen darüber, wo und wie Benutzer Unterstützung erhalten können (z.B. Forum, E-Mail-Support).
Fehlerberichterstattung: Wie können Nutzer Bugs melden oder Feature-Anfragen stellen?

## 1.10. FAQs und Troubleshooting

Häufige Fragen: Antworten auf häufige Fragen zur Nutzung der API.
Fehlerbehebung: Leitfaden zur Behebung häufiger Probleme.

## 1.11. Interaktive Dokumentation (optional)

Swagger/OpenAPI: Ein interaktives Interface, mit dem Entwickler API-Endpunkte direkt aus der Dokumentation heraus testen können.
API-Sandbox: Eine Testumgebung, in der Entwickler sicher mit der API experimentieren können.
Eine gut strukturierte API-Dokumentation erleichtert es Entwicklern, die API effizient zu nutzen, und trägt dazu bei, häufige Fragen und Probleme zu minimieren.

## 1.12. Changelog

Ein detaillierter Verlauf der Änderungen an der API.

## 1.13. git Branch Modell

In diesem Repository werden Branches verwendet um den Status der Weiterentwicklung und das Review von Änderungen abzubilden.

Folgende Branches werden verwendet

- *main* (enthält den letzten freigegebenen Stand der Entwicklung; besteht permanent)
- *develop* (enthält den Stand der fertig entwickelten Features und wird zum Review durch Industriepartner und Gesellschafter verwendet; basiert auf main; nach Freigabe erfolgt ein merge in main und ein Release wird erzeugt; besteht permanent)
- *feature/[name]* (in feature branches werden neue Features entwickelt; basiert auf develop; nach Fertigstellung erfolgt ein merge in develop; wird nach dem merge gelöscht)
- *hotfix/[name]* (in hotfix branches werden Hotfixes entwickelt; basiert auf main; nach Fertigstellung erfolgt ein merge in develop und in main; wird nach dem merge gelöscht)
- *concept/[name]* (in feature branches werden neue Konzepte entwickelt; basiert auf develop; dient der Abstimmung mit Dritten; es erfolgt kein merge; wird nach Bedarf gelöscht)
- *misc/[name]* (nur für internen Gebrauch der gematik; es erfolgt kein merge; wird nach Bedarf gelöscht)

## 1.14. Lizenzbedingungen

Copyright (c) 2024 gematik GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
