# OAuth 2.0 Authorization Server API Documentation

## Inhaltsverzeichnis
- [OAuth 2.0 Authorization Server API Documentation](#oauth-20-authorization-server-api-documentation)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [1. Einleitung](#1-einleitung)
  - [2. Well-Known Endpoint](#2-well-known-endpoint)
  - [3. Authorization Endpoint](#3-authorization-endpoint)
  - [4. Token Endpoint](#4-token-endpoint)
  - [5. JWKS Endpoint](#5-jwks-endpoint)
  - [6. Client Registration Endpoint](#6-client-registration-endpoint)
    - [a) Create (Registrierung eines neuen Clients)](#a-create-registrierung-eines-neuen-clients)
    - [b) Read (Abfrage eines registrierten Clients)](#b-read-abfrage-eines-registrierten-clients)
    - [c) Update (Aktualisierung eines registrierten Clients)](#c-update-aktualisierung-eines-registrierten-clients)

## 1. Einleitung
Diese API-Dokumentation beschreibt die Endpunkte eines OAuth 2.0 Authorization Servers, der OpenID Connect (OIDC) und den Authorization Code Flow mit Proof Key for Code Exchange (PKCE), Pushed Authorization Requests (PAR) und DPoP unterstützt.

---

## 2. Well-Known Endpoint

**Pfad:** `/.well-known/oauth-authorization-server`

- **Beschreibung:** Ermöglicht die Abfrage des OAuth 2.0 Authorization Server Metadata.
- **Methoden:** `GET`

- **Beispiel Request:**

  ```http
  GET /.well-known/oauth-authorization-server HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "issuer": "https://auth.example.com",
    "authorization_endpoint": "https://auth.example.com/auth",
    "token_endpoint": "https://auth.example.com/token",
    "jwks_uri": "https://auth.example.com/jwks",
    "response_types_supported": ["code", "token", "id_token"],
    "subject_types_supported": ["public"]
  }
  ```

---

## 3. Authorization Endpoint

**Pfad:** `/auth`

- **Beschreibung:** Dieser Endpunkt unterstützt OIDC, den Authorization Code Flow mit PKCE, Pushed Authorization Requests und DPoP. Nach erfolgreicher Authentifizierung erstellt er Access- und Refresh-Tokens.
- **Methoden:** `GET`, `POST`
- **Unterstützte Verfahren:**
  - **Client Assertion JWT**
  - **DPoP**

- **Beispiel Request (Authorization Code Flow):**

  ```http
  GET /auth?response_type=code&client_id=s6BhdRkqt3&redirect_uri=https://client.example.com/cb&scope=openid&state=af0ifjsldkj HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response (Erfolg):**

  ```http
  HTTP/1.1 302 Found
  Location: https://client.example.com/cb?code=SplxlOBeZQQYbYS6WxSbIA&state=af0ifjsldkj
  ```

---

## 4. Token Endpoint

**Pfad:** `/token`

- **Beschreibung:** Dieser Endpunkt ermöglicht den Austausch eines Authorization Codes oder Refresh Tokens in ein neues Access- und Refresh-Token.
- **Methoden:** `POST`

- **Beispiel Request (Exchange mit Refresh Token):**

  ```http
  POST /token HTTP/1.1
  Host: auth.example.com
  Content-Type: application/x-www-form-urlencoded

  grant_type=refresh_token&refresh_token=tGzv3JOkF0XG5Qx2TlKWIA&client_id=s6BhdRkqt3
  ```

- **Beispiel Response (Erfolg):**

  ```json
  {
    "access_token": "mF_9.B5f-4.1JqM",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
    "scope": "openid"
  }
  ```

---

## 5. JWKS Endpoint

**Pfad:** `/jwks`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage der Signatur-Zertifikate (JWKS).
- **Methoden:** `GET`

- **Beispiel Request:**

  ```http
  GET /jwks HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "keys": [
      {
        "kty": "RSA",
        "use": "sig",
        "kid": "1b94c",
        "e": "AQAB",
        "n": "wgg4_Gnrx1..."
      }
    ]
  }
  ```

---

## 6. Client Registration Endpoint

**Pfad:** `/clientreg`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Verwaltung von OAuth 2.0 Clients. Er unterstützt die Registrierung, Abfrage, Aktualisierung und Löschung von Clients mittels sicherer Authentifizierungsverfahren. Clients werden nach dem Schema `ClientInstance` registriert.

### a) Create (Registrierung eines neuen Clients)

- **Methoden:** `POST`
- **Unterstützte Verfahren:**
  - **Android Key ID Attestation (für Google-Android Geräte)**
  - **Apple DCAppAttest**
  - **Signiertes Client Assertion JWT**
  - **TPM signiertes Client Assertion JWT**
  - **ClientZertifikat plus Client Assertion JWT** (nur für Dienst-zu-Dienst Kommunikation)

- **Beispiel Request:**

  ```http
  POST /clientreg HTTP/1.1
  Host: auth.example.com
  Content-Type: application/json

  {
    "name": "MyClientInstance",
    "client_id": "s6BhdRkqt3",
    "product_id": "com.example.myapp",
    "product_name": "MyApp",
    "product_version": "1.0.0",
    "manufacturer_id": "com.example",
    "manufacturer_name": "Example Inc.",
    "owner": {
      "id": "user-123",
      "gesundheitsid": "1234567890"
    },
    "owner_mail": "user@example.com",
    "registration_timestamp": 1625465461,
    "platform": "Android",
    "posture": {
      "integrity": "high",
      "encryption": "AES-256"
    },
    "attestation": {
      "type": "AndroidKey",
      "certificate": "MIICmzCCAi..."
    }
  }
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "client_id": "s6BhdRkqt3",
    "client_secret": "cf136dc3c4f1a4a6453d"
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "invalid_client_metadata",
    "error_description": "The client metadata is invalid."
  }
  ```

### b) Read (Abfrage eines registrierten Clients)

- **Methoden:** `GET`
- **Beschreibung:** Ruft die Details eines registrierten Clients ab.
- **Parameter:**
  - **client_id (string, erforderlich):** Die eindeutige Kennung des Clients.

- **Beispiel Request:**

  ```http
  GET /clientreg?client_id=s6BhdRkqt3 HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "name": "MyClientInstance",
    "client_id": "s6BhdRkqt3",
    "product_id": "com.example.myapp",
    "product_name": "MyApp",
    "product_version": "1.0.0",
    "manufacturer_id": "com.example",
    "manufacturer_name": "Example Inc.",
    "owner": {
      "id": "user-123",
      "gesundheitsid": "1234567890"
    },
    "owner_mail": "user@example.com",
    "registration_timestamp": 1625465461,
    "platform": "Android",
    "posture": {
      "integrity": "high",
      "encryption": "AES-256"
    },
    "attestation": {
      "type": "AndroidKey",
      "certificate": "MIICmzCCAi..."
    }
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "client_not_found",
    "error_description": "The specified client could not be found."
  }
  ```

### c) Update (Aktualisierung eines registrierten Clients)

- **Methoden:** `PUT`
- **Beschreibung:** Aktualisiert die Metadaten eines registrierten Clients.
- **Parameter:**
  - **client_id (string, erforderlich):** Die eindeutige Kennung des Clients.
  - **client_assertion (string, erforderlich):** JWT zur Authentifizierung des Clients.

- **Beispiel Request:**

  ```http
  PUT /clientreg HTTP/1.1
  Host: auth.example.com
  Content-Type: application/json

  {
    "client_id": "s6BhdRkqt3",
    "name": "UpdatedMyClientInstance",
    "product_id": "com.example.myapp",
    "product_name": "MyUpdatedApp",
    "product_version": "1.1.0",
    "manufacturer_id": "com.example",
    "manufacturer_name": "Example