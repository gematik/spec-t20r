![gematik logo](/images/gematik_logo.svg)

# ZETA API

## 1.1. Einführung

Die ZETA API ermöglicht es ZETA Clients, auf geschützte Ressourcen zuzugreifen und dabei Sicherheits- und Authentifizierungsmechanismen zu nutzen.
Diese API nutzt Endpunkte des ZETA Guard für die Client-Registrierung, Authentifizierung und Autorisierung.

Stationäre Clients verwenden bei der Registrierung und bei der Authentifizierung Endpunkte des Konnektors/TI-Gateways und des ZETA Attestation Service.

Mobile Clients verwenden bei der Registrierung Endpunkte der betriebssystem-spezifischen Attestierung. Die Authentifizierung erfolgt mit OpenID Connect (OIDC) und der ZETA Guard API.

Die ZETA API ist so konzipiert, dass sie eine sichere und flexible Interaktion zwischen ZETA Clients und geschützten Ressourcen ermöglicht. Sie basiert auf den Standards des OAuth 2.0 Frameworks und erweitert diese um spezifische Anforderungen der gematik.

---

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
        - [1.5.1.1.1 Anfragen](#15111-anfragen)
        - [1.5.1.2.2 Antworten](#15122-antworten)
      - [1.5.1.2 Authorization Server Well-Known Endpoint](#1512-authorization-server-well-known-endpoint)
        - [1.5.1.2.1 Anfragen](#15121-anfragen)
        - [1.5.1.2.2 Antworten](#15122-antworten-1)
      - [1.5.1.3 Nonce Endpoint](#1513-nonce-endpoint)
        - [1.5.1.3.1 Anfragen](#15131-anfragen)
        - [1.5.1.3.2 Antworten](#15132-antworten)
      - [1.5.1.4 Dynamic Client Registration Endpoint](#1514-dynamic-client-registration-endpoint)
        - [1.5.1.4.1 Anfragen für stationäre Clients](#15141-anfragen-für-stationäre-clients)
        - [1.5.1.4.2 Antworten](#15142-antworten)
      - [1.5.1.5 Token Endpoint](#1515-token-endpoint)
        - [1.5.1.5.1 Anfragen](#15151-anfragen)
        - [1.5.1.5.2 Antworten](#15152-antworten)
      - [1.5.1.6 Resource Endpoint](#1516-resource-endpoint)
        - [1.5.1.6.1 Anfragen](#15161-anfragen)
        - [1.5.1.6.2 Antworten](#15162-antworten)
      - [1.5.1.7 JWKS Endpoint](#1517-jwks-endpoint)
        - [1.5.1.7.1 Anfragen](#15171-anfragen)
        - [1.5.1.7.2 Antworten](#15172-antworten)
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

##### 1.5.1.1.1 Anfragen

Der Endpunkt wird über eine einfache HTTP GET-Anfrage ohne Body aufgerufen.

```http
GET /.well-known/oauth-protected-resource HTTP/1.1
Host: api.example.com
Accept: application/json
```

---

##### 1.5.1.2.2 Antworten

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
  "type": "https://httpstatuses.com/404",
  "title": "OAuth Protected Resource Configuration Not Found",
  "status": 404,
  "detail": "The requested OAuth Protected Resource Well-Known configuration could not be found at this path.",
  "instance": "/.well-known/oauth-protected-resource"
}
```

- **500 Internal Server Error:**
  - **Bedeutung:** Ein unerwarteter Fehler ist auf dem Server der Protected Resource aufgetreten, der die Verarbeitung der Anfrage verhindert hat.
  - **Beispielantwort:** Ein leerer Body, ein generischer 
Content-Type: application/problem+json

```json
{
  "type": "https://httpstatuses.com/500",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred while processing your request.",
  "instance": "/.well-known/oauth-protected-resource"
}
```

---

#### 1.5.1.2 Authorization Server Well-Known Endpoint

Dieser Endpunkt ermöglicht Clients und anderen Parteien die einfache Entdeckung der Konfigurationsmetadaten eines OAuth 2.0 Autorisierungsservers (AS) und seiner Fähigkeiten. Er ist gemäß RFC 8414 definiert und bietet eine standardisierte Methode, um Informationen wie Endpunkt-URIs, unterstützte Grant Types und Scopes abzurufen, ohne diese manuell konfigurieren zu müssen.

---

##### 1.5.1.2.1 Anfragen

Dieser Endpunkt wird über eine HTTP GET-Anfrage ohne Parameter aufgerufen.

**Methode:**
`GET`

**Header:**
Ein `Accept`-Header mit `application/json` wird empfohlen, um die bevorzugte Antwortformat anzugeben.

**Beispiel Anfrage:**

```http
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: api.example.com
Accept: application/json
```

---

##### 1.5.1.2.2 Antworten

**Statuscodes:**

- **200 OK:**
  - **Bedeutung:** Die Anfrage war erfolgreich, und der Server gibt die Konfigurationsmetadaten des Autorisierungsservers als JSON-Objekt zurück.
  - **Content-Type:** `application/json`
  - **Beispiel Antwort:**

```json
{
  "issuer": "https://api.example.com",
  "authorization_endpoint": "https://api.example.com/auth",
  "token_endpoint": "https://api.example.com/token",
  "jwks_uri": "https://api.example.com/certs",
  "response_types_supported": [
    "code",
    "token"
  ],
  "response_modes_supported": [
    "query",
    "fragment",
    "form_post"
  ],
  "grant_types_supported": [
    "authorization_code",
    "token-exchange",
    "refresh_token"
  ],
  "token_endpoint_auth_methods_supported": [
    "private_key_jwt"
  ],
  "token_endpoint_auth_signing_alg_values_supported": [
    "ES256"
  ],
  "service_documentation": "https://api.example.com/docs",
  "code_challenge_methods_supported": [
    "S256"
  ]
}
```

**404 Not Found:**

**Content-Type:**
`application/problem+json`

Dies tritt auf, wenn der Endpunkt unter der angefragten URL nicht gefunden werden kann.

```json
{
  "type": "https://httpstatuses.com/404",
  "title": "Not Found",
  "status": 404,
  "detail": "The requested resource was not found on this server.",
  "instance": "/.well-known/oauth-authorization-server"
}
```

**500 Internal Server Error:**

**Content-Type:**
`application/problem+json`

Dies tritt auf, wenn ein unerwarteter Fehler auf dem Server auftritt, der die Anfrage nicht verarbeiten konnte.

```json
{
  "type": "https://httpstatuses.com/500",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred while processing your request.",
  "instance": "/.well-known/oauth-authorization-server"
}
```

---

#### 1.5.1.3 Nonce Endpoint

Dieser Endpunkt ermöglicht Clients das Abrufen eines einmaligen kryptographischen Werts, einer sogenannten "Nonce". Die Nonce dient in der Regel dem Schutz vor Replay-Angriffen und wird typischerweise von OpenID Connect Clients verwendet, um die Integrität und Einmaligkeit von ID-Tokens zu gewährleisten. Der Client sendet die erhaltene Nonce als Parameter an den Autorisierungs-Endpunkt, und der Authorization Server gibt sie unverändert im ID-Token zurück. Der Client kann dann überprüfen, ob die Nonce im ID-Token mit der ursprünglich gesendeten übereinstimmt.

---

##### 1.5.1.3.1 Anfragen

**Beispiel Anfrage:**

```http
GET /nonce HTTP/1.1
Host: api.example.com
Accept: application/json
```

---

##### 1.5.1.3.2 Antworten

**Statuscodes:**

- **200 OK:**
  - **Bedeutung:** Die Anfrage war erfolgreich, und der Server gibt die Nonce als JSON-Objekt zurück.
  - **Content-Type:** `application/json`
  - **Beispiel Antwort:**

```json
{
  "nonce": "s.fRzE3M0J_QxL-x.6gA~x",
  "expires_in": 300
}
```

**Felder der erfolgreichen Antwort:**

*   `nonce` (String): Der generierte, einmalige kryptographische Wert.
*   `expires_in` (Integer): Die Gültigkeitsdauer der Nonce in Sekunden, ab dem Zeitpunkt der Ausstellung. Nach Ablauf dieser Zeit sollte die Nonce vom Server nicht mehr akzeptiert werden.

**404 Not Found:**

**Content-Type:**
`application/problem+json`

Dies tritt auf, wenn der Endpunkt unter der angefragten URL nicht gefunden werden kann.

```json
{
  "type": "https://httpstatuses.com/404",
  "title": "Not Found",
  "status": 404,
  "detail": "The requested resource was not found on this server.",
  "instance": "/nonce"
}
```

**429 Too Many Requests:**

Dieser Fehler tritt auf, wenn der Client die vom Server festgelegten Ratenbegrenzungen überschreitet.

**Content-Type:**
`application/problem+json`

**Retry-After: 60**

```json
{
  "type": "tag:authorization.example.com,2023:oauth:nonce:rate_limit_exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the allowed number of nonce requests. Please try again after 60 seconds.",
  "instance": "/nonce"
}
```

*   `Retry-After` Header (optional): Gibt an, wie viele Sekunden der Client warten sollte, bevor er eine weitere Anfrage stellt.


**500 Internal Server Error:**

**Content-Type:**
`application/problem+json`

Dies tritt auf, wenn ein unerwarteter Fehler auf dem Server auftritt, der die Anfrage nicht verarbeiten konnte.

```json
{
  "type": "https://httpstatuses.com/500",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred while processing your request.",
  "instance": "/nonce"
}
```

---

#### 1.5.1.4 Dynamic Client Registration Endpoint

Dieser Endpunkt ermöglicht die dynamische Registrierung neuer OAuth 2.0 Clients beim Authorization Server. Im Unterschied zur standardisierten dynamischen Client-Registrierung gemäß RFC 7591 erfordert dieser Endpunkt eine zusätzliche Validierung in Form eines `software_statement`, das TPM-Attestierungsnachweise und Software-Metadaten enthält. Die Registrierung muss über eine TLS-geschützte Verbindung erfolgen.

---

##### 1.5.1.4.1 Anfragen für stationäre Clients

Der Client sendet eine `POST`-Anfrage an den `/register`-Endpunkt. Der Anfrage-Body ist ein JSON-Objekt, das die Metadaten des zu registrierenden Clients enthält.

Neben den Standard-Client-Metadaten gemäß RFC 7591 ist ein `software_statement` erforderlich, das den spezifischen Anforderungen des [Dynamic Client Registration-Ablaufs](https://raw.githubusercontent.com/gematik/spec-t20r/refs/heads/develop/images/tpm-attestation-and-token-exchange/dynamic-client-registration-with-tpm-attestation.svg) entspricht. Das `software_statement` ist ein signiertes JWT (JSON Web Token), das die Identität der Software und zusätzliche Attestierungsnachweise enthält. Es muss mit dem Private Key der Client-Instanz signiert sein.

**Erforderliche Parameter im Anfrage-Body:**

| Parameter                   | Typ      | Beschreibung                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| :-------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `redirect_uris`             | `array`  | Eine Liste von Redirection-URI-Strings, die der Client für die Weiterleitung von Autorisierungsantworten verwendet. Muss mindestens eine URI enthalten.                                                                                                                                                                                                                                                                                                              |
| `grant_types`               | `array`  | Eine Liste der unterstützten Grant Types. Empfohlene Werte sind `authorization_code`, `client_credentials`, `refresh_token`.                                                                                                                                                                                                                                                                                                                                        |
| `software_statement`        | `string` | Ein JWS Compact Serialization string (JWT), der vom Software-Anbieter signiert ist. Dieses JWT muss folgende Claims enthalten: <br> - `software_id` (String): Eine eindeutige ID der Software (z.B. UUID). <br> - `software_version` (String): Die Version der Software. <br> - `organisation_id` (String): Die ID der Organisation, die die Software bereitstellt. <br> - `software_jwk_set` (JSON Object) oder `software_jwk_set_uri` (String): Der Public Key (Set) der Software, typischerweise für die Validierung von Signaturen der Software selbst. <br> - `attestation_cert_chain` (Array of Strings): Eine Kette von PEM-enkodierten X.509-Zertifikaten, die den Nachweis der TPM-Attestierung ermöglichen. <br> - `attestation_jwt` (String): Ein weiteres JWT, das den eigentlichen TPM-Attestierungsnachweis enthält (oft ein Verifiable Credential oder ähnliches). |
| `jwks` | `string` | Client's JSON Web Key Set [RFC7517] Dokument, dass den Client Public Key enthält.

**Optionale Parameter im Anfrage-Body (gemäß RFC 7591):**

| Parameter                     | Typ      | Beschreibung                                                                                |
| :---------------------------- | :------- | :------------------------------------------------------------------------------------------ |
| `client_name`                 | `string` | Name des Clients, der den Endbenutzern angezeigt werden kann.                               |
| `token_endpoint_auth_method`  | `string` | Authentisierungsmethode am Token-Endpunkt. Standard ist `private_key_jwt`.             |

**Beispiel Anfrage:**

**POST /register:**

**Content-Type:** `application/json`**

```json
{
  "redirect_uris": [
    "https://client.example.org/cb",
    "https://client.example.org/callback"
  ],
  "client_name": "Mein Client",
  "token_endpoint_auth_method": "private_key_jwt",
  "grant_types": [
    "urn:ietf:params:oauth:grant-type:token-exchange",
    "refresh_token"
  ],
  "jwks": {
    "keys": [ <Client_Instance_Public_Key_JWK> ]
  },
  "urn:gematik:params:oauth:client-attestation-type:tpm2": {
    "client_statement": "<Base64(Client Statement JWT)>",
    "client_statement_format": "client-statement-jwt"
  }
}

```

##### 1.5.1.4.2 Antworten

Der Authorization Server antwortet mit verschiedenen HTTP-Statuscodes und entsprechenden JSON-Objekten, die entweder die erfolgreiche Registrierung oder Fehlermeldungen gemäß RFC 9457 ("Problem Details for HTTP APIs") beschreiben.

**Statuscodes:**

- **201 Created:**
  - **Bedeutung:** Die Registrierung war erfolgreich, und der Server gibt die Client-ID und andere Metadaten des registrierten Clients zurück.
  - **Content-Type:** `application/json`
  - **Beispiel Antwort:**

```json
{
  "client_id": "1234567890abcdef",
  "client_id_issued_at": 1678886400,
  "grant_types": [
    "token-exchange",
    "refresh_token"
  ],
  "token_endpoint_auth_method": "private_key_jwt",
  "redirect_uris": [
    "https://client.example.org/cb",
    "https://client.example.org/callback"
  ],
  "client_name": "Mein Client",
  "jwks": {
    "keys": [
      {
        "kty": "EC",
        "crv": "P-256",
        "x": "x-coordinate",
        "y": "y-coordinate",
        "use": "sig"
      }
    ]
  },
  "urn:gematik:params:oauth:client-attestation-type:tpm2": {
    "client_statement": "<Base64(Client Statement JWT)>",
    "client_statement_format": "client-statement-jwt"
  }
}
```

- **400 Bad Request:**
  - **Bedeutung:** Die Anfrage war fehlerhaft, z.B. fehlende oder ungültige Parameter.
  - **Content-Type:** `application/problem+json`
  - **Beispiel Antwort:**

```json
{
  "type": "https://httpstatuses.com/400",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid request parameters. Please check your input.",
  "instance": "/register"
}
```

- **409 Conflict  :**
  - **Bedeutung:** Ein Client mit der angegebenen `software_statement` existiert bereits.
  - **Content-Type:** `application/problem+json`
  - **Beispiel Antwort:**

```json
{
  "type": "https://httpstatuses.com/409",
  "title": "Conflict",
  "status": 409,
  "detail": "A client with the provided software statement already exists.",
  "instance": "/register"
}
```

- **500 Internal Server Error:**
  - **Bedeutung:** Ein unerwarteter Fehler ist auf dem Server aufgetreten, der die Anfrage nicht verarbeiten konnte.
  - **Content-Type:** `application/problem+json`
  - **Beispiel Antwort:**
```json
{
  "type": "https://httpstatuses.com/500",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred while processing your request.",
  "instance": "/register"
}
```

---


#### 1.5.1.5 Token Endpoint

##### 1.5.1.5.1 Anfragen

##### 1.5.1.5.2 Antworten

#### 1.5.1.6 Resource Endpoint

##### 1.5.1.6.1 Anfragen

##### 1.5.1.6.2 Antworten

#### 1.5.1.7 JWKS Endpoint

##### 1.5.1.7.1 Anfragen

##### 1.5.1.7.2 Antworten

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
