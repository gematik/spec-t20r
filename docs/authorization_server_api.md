
# OAuth 2.0 Authorization Server API Dokumentation

## Übersicht

Diese API bietet Endpunkte zur Unterstützung der OAuth 2.0 und OpenID Connect (OIDC) Protokolle. Die API unterstützt mehrere Authentifizierungs- und Autorisierungsmechanismen, einschließlich Authorization Code Flow mit Proof Key for Code Exchange (PKCE), Pushed Authorization Requests (PAR), und Demonstration of Proof-of-Possession (DPoP). Sie bietet außerdem Client-Registrierungsoptionen für verschiedene Geräte und Authentifizierungsmethoden.

## Endpunkte

### 1. Well-Known Dokument

**Pfad:** `/.well-known/oauth-authorization-server`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage des Well-Known Dokuments, das Konfigurationsdetails des Authorization Servers bereitstellt.
- **Methoden:** `GET`
- **Beispiel Request:**

  ```http
  GET /.well-known/oauth-authorization-server HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  ```json
  {
    "issuer": "https://auth.example.com",
    "authorization_endpoint": "https://auth.example.com/auth",
    "token_endpoint": "https://auth.example.com/token",
    "jwks_uri": "https://auth.example.com/jwks",
    "response_types_supported": ["code", "id_token", "token"],
    "grant_types_supported": ["authorization_code", "refresh_token"],
    "subject_types_supported": ["public"],
    "id_token_signing_alg_values_supported": ["RS256"]
  }
  ```

- **Relevanter RFC:** [RFC 8414 - OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)

### 2. Authorization Endpoint

**Pfad:** `/auth`

- **Beschreibung:** Dieser Endpunkt unterstützt den OpenID Connect (OIDC) Flow und den OAuth 2.0 Authorization Code Flow mit PKCE und Pushed Authorization Requests (PAR). Er unterstützt auch Client Assertion JWTs und DPoP für die sichere Token-Anfrage. Nach erfolgreicher Authentifizierung erstellt der Server Access- und Refresh-Tokens.
- **Methoden:** `GET`, `POST`
- **Unterstützte Flows:**
  - **Authorization Code Flow mit PKCE**
  - **OpenID Connect (OIDC)**
  - **Pushed Authorization Requests (PAR)**

- **Authentifizierung:**
  - **Client Assertion JWT**
  - **DPoP (Demonstration of Proof-of-Possession)**

- **Beispiel Request:**

  ```http
  GET /auth?response_type=code&client_id=your-client-id&redirect_uri=https%3A%2F%2Fclient.example.com%2Fcallback&scope=openid%20profile%20email&state=xyzABC123&code_challenge=challenge&code_challenge_method=S256 HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```http
  HTTP/1.1 302 Found
  Location: https://client.example.com/callback?code=SplxlOBeZQQYbYS6WxSbIA&state=xyzABC123
  ```

  **Fehler:**

  ```http
  HTTP/1.1 400 Bad Request
  Content-Type: application/json

  {
    "error": "invalid_request",
    "error_description": "Missing required parameter: redirect_uri"
  }
  ```

- **Relevante RFCs und Standards:**
  - [RFC 6749 - Authorization Code Flow](https://datatracker.ietf.org/doc/html/rfc6749)
  - [RFC 7636 - PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
  - [RFC 9126 - PAR](https://datatracker.ietf.org/doc/html/rfc9126)
  - [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

### 3. Token Endpoint

**Pfad:** `/token`

- **Beschreibung:** Ermöglicht den Tausch eines Refresh-Tokens gegen ein neues Access- und Refresh-Token. Unterstützt auch Client Assertion JWTs und DPoP.
- **Methoden:** `POST`
- **Anfragetypen:** `application/x-www-form-urlencoded`
- **Erforderliche Parameter:**
  - **grant_type (string, erforderlich):** Der Typ des Antrags, hier `refresh_token`.
  - **refresh_token (string, erforderlich):** Das aktuelle Refresh-Token, das getauscht werden soll.
  - **client_assertion (string, optional):** JWT, das den Client für die Anfrage authentifiziert.
  - **client_assertion_type (string, optional):** Der Typ des JWT-Assertions, in der Regel `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`.
  - **dpop (string, optional):** DPoP-Proof JWT, das die Bindung eines Tokens an ein spezifisches HTTP-Anforderungsobjekt beweist.

- **Beispiel Request:**

  ```http
  POST /token HTTP/1.1
  Host: auth.example.com
  Content-Type: application/x-www-form-urlencoded

  grant_type=refresh_token&refresh_token=tGzv3JOkF0XG5Qx2TlKWIA&client_assertion=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "access_token": "mF_9.B5f-4.1JqM",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA"
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "invalid_request",
    "error_description": "Invalid refresh token"
  }
  ```

- **Relevante RFCs:**
  - [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
  - [RFC 7523 - Client Assertion JWT](https://datatracker.ietf.org/doc/html/rfc7523)
  - [DPoP Entwurf](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-dpop)

### 4. JWKS Endpoint

**Pfad:** `/jwks`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage der öffentlichen Signaturschlüssel, die vom Authorization Server verwendet werden, um Tokens zu signieren.
- **Methoden:** `GET`
- **Beispiel Request:**

  ```http
  GET /jwks HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  ```json
  {
    "keys": [
      {
        "kty": "RSA",
        "kid": "1b94c",
        "use": "sig",
        "n": "vrjOf1NJr...5IQ",
        "e": "AQAB",
        "alg": "RS256"
      }
    ]
  }
  ```

- **Relevanter RFC:** [RFC 7517 - JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517)

### 5. Nonce Endpoint

**Pfad:** `/nonce`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage einer neuen Nonce, die für sicherheitsrelevante Transaktionen genutzt werden kann.
- **Methoden:** `GET`
- **Beispiel Request:**

  ```http
  GET /nonce HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  ```json
  {
    "nonce": "n-0S6_WzA2Mj"
  }
  ```


### 6. Client Registration Endpoint

**Pfad:** `/clientreg`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Verwaltung von OAuth 2.0 Clients. Er unterstützt die Registrierung, Abfrage, Aktualisierung und Löschung von Clients mittels sicherer Authentifizierungsverfahren.

#### a) Create (Registrierung eines neuen Clients)

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
    "client_name": "MyApp",
    "redirect_uris": ["https://myapp.example.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"],
    "client_assertion": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
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

#### b) Read (Abfrage eines registrierten Clients)

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
    "client_id": "s6BhdRkqt3",
    "client_name": "MyApp",
    "redirect_uris": ["https://myapp.example.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"]
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "client_not_found",
    "error_description": "The specified client could not be found."
  }
  ```

#### c) Update (Aktualisierung eines registrierten Clients)

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
    "client_name": "UpdatedMyApp",
    "redirect_uris": ["https://updatedmyapp.example.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"],
    "client_assertion": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "client_id": "s6BhdRkqt3",
    "client_name": "UpdatedMyApp",
    "redirect_uris": ["https://updatedmyapp.example.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"]
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "invalid_client_assertion",
    "error_description": "The client assertion is invalid or expired."
  }
  ```

#### d) Delete (Löschung eines registrierten Clients)

- **Methoden:** `DELETE`
- **Beschreibung:** Löscht einen registrierten Client.
- **Parameter:**
  - **client_id (string, erforderlich):** Die eindeutige Kennung des Clients.
  - **client_assertion (string, erforderlich):** JWT zur Authentifizierung des Clients.

- **Beispiel Request:**

  ```http
  DELETE /clientreg?client_id=s6BhdRkqt3 HTTP/1.1
  Host: auth.example.com
  Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "status": "client_deleted",
    "client_id": "s6BhdRkqt3"
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "client_not_found",
    "error_description": "The specified client could not be found or has already been deleted."
  }
  ```

#### e) Interner Endpoint zur Abfrage von Client-Daten

**Pfad:** `/clientreg/internal`

- **Beschreibung:** Dieser interne Endpunkt ermöglicht es dem HTTP-Proxy, Client-Daten basierend auf der `cid` (Client ID) abzufragen.
- **Methoden:** `GET`
- **Parameter:**
  - **cid (string, erforderlich):** Die Client ID, für die die Daten abgefragt werden sollen.

- **Beispiel Request:**

  ```http
  GET /clientreg/internal?cid=s6BhdRkqt3 HTTP/1.1
  Host: auth.example.com
  ```

- **Beispiel Response:**

  **Erfolg:**

  ```json
  {
    "cid": "s6BhdRkqt3",
    "client_name": "MyApp",
    "redirect_uris": ["https://myapp.example.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"]
  }
  ```

  **Fehler:**

  ```json
  {
    "error": "client_not_found",
    "error_description": "The specified client could not be found."
  }
  ```

- **Hinweis:** Dieser Endpunkt ist nur für interne Systeme bestimmt und sollte nicht öffentlich zugänglich gemacht werden.

