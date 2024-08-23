# OAuth 2.0 Authorization Server API Dokumentation

## Übersicht

Diese API bietet Endpunkte zur Unterstützung der OAuth 2.0 und OpenID Connect (OIDC) Protokolle. Die API unterstützt mehrere Authentifizierungs- und Autorisierungsmechanismen, einschließlich Authorization Code Flow mit Proof Key for Code Exchange (PKCE), Pushed Authorization Requests (PAR), und Demonstration of Proof-of-Possession (DPoP). Sie bietet außerdem Client-Registrierungsoptionen für verschiedene Geräte und Authentifizierungsmethoden.

## Endpunkte

### 1. Well-Known Dokument

**Pfad:** `/.well-known/oauth-authorization-server`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage des Well-Known Dokuments, das Konfigurationsdetails des Authorization Servers bereitstellt.
- **Methoden:** `GET`
- **Beispiel Request:** *noch nicht geprüft*

  ```http
  GET /.well-known/oauth-authorization-server HTTP/1.1
  Host: auth.example.com


- **Antworten:**
  - **200 OK**
    - **Content-Type:** `application/json`
    - **Beispiel Response:** *noch nicht geprüft*

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

    - **Beschreibung:** Liefert das Well-Known Dokument mit den Metadaten des Authorization Servers.
    - **Relevanter RFC:** [RFC 8414 - OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)

### 2. Authorization Endpoint

**Pfad:** `/auth`

- **Beschreibung:** Dieser Endpunkt unterstützt den OpenID Connect (OIDC) Flow und den OAuth 2.0 Authorization Code Flow mit PKCE und Pushed Authorization Requests (PAR). Er unterstützt auch Client Assertion JWTs und DPoP für die sichere Token-Anfrage. Nach erfolgreicher Authentifizierung erstellt der Server Access- und Refresh-Tokens.
- **Methoden:** `GET`, `POST`
- **Unterstützte Flows:**
  - **Authorization Code Flow mit PKCE**
    - **Relevanter RFC:** [RFC 7636 - Proof Key for Code Exchange by OAuth Public Clients](https://datatracker.ietf.org/doc/html/rfc7636)
  - **OpenID Connect (OIDC)**
    - **Relevanter Standard:** [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
  - **Pushed Authorization Requests (PAR)**
    - **Relevanter RFC:** [RFC 9126 - OAuth 2.0 Pushed Authorization Requests](https://datatracker.ietf.org/doc/html/rfc9126)

- **Authentifizierung:**
  - **Client Assertion JWT**
    - **Relevanter RFC:** [RFC 7523 - JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants](https://datatracker.ietf.org/doc/html/rfc7523)
  - **DPoP (Demonstration of Proof-of-Possession)**
    - **Relevanter Entwurf:** [OAuth 2.0 Demonstration of Proof-of-Possession at the Application Layer (DPoP)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-dpop)

- **Wichtige Parameter:**
  - **response_type (string, erforderlich):** Gibt den gewünschten Autorisierungstyp an. Meistens auf `code` gesetzt für den Authorization Code Flow. ([RFC 6749, Abschnitt 4.1.1](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1))
  - **client_id (string, erforderlich):** Die Client-ID, die der Anwendung zugewiesen wurde. ([RFC 6749, Abschnitt 4.1.1](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1))
  - **redirect_uri (string, optional):** Die Umleitungs-URI, an die die Antwort gesendet wird. Muss mit einer der beim Client registrierten URIs übereinstimmen. ([RFC 6749, Abschnitt 4.1.1](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1))
  - **scope (string, optional):** Ein durch Leerzeichen getrennter Satz von Berechtigungen, die angefordert werden. ([RFC 6749, Abschnitt 3.3](https://datatracker.ietf.org/doc/html/rfc6749#section-3.3))
  - **state (string, optional):** Ein Wert, den der Client zur Wahrung des Zustands zwischen Anfragen und Antworten nutzt. ([RFC 6749, Abschnitt 4.1.1](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1))
  - **code_challenge (string, optional):** Der PKCE-Code-Herausforderung für Public Clients. ([RFC 7636, Abschnitt 4.2](https://datatracker.ietf.org/doc/html/rfc7636#section-4.2))
  - **code_challenge_method (string, optional):** Die Methode zur Erstellung des `code_challenge`. Üblicherweise `S256`. ([RFC 7636, Abschnitt 4.2](https://datatracker.ietf.org/doc/html/rfc7636#section-4.2))
  - **request_uri (string, optional):** Ein URI, der auf einen zuvor registrierten Autorisierungsanforderung verweist. Genutzt für PAR. ([RFC 9126, Abschnitt 2.2](https://datatracker.ietf.org/doc/html/rfc9126#section-2.2))

  - **Beispiel für OIDC und OAuth 2 Authorization Code Flow** *noch nicht geprüft*

    ```http
    GET /auth?response_type=code&client_id=your-client-id&redirect_uri=https%3A%2F%2Fclient.example.com%2Fcallback&scope=openid%20profile%20email&state=xyzABC123&code_challenge=challenge&code_challenge_method=S256 HTTP/1.1
    Host: auth.example.com
    ```

- **Antworten:**
  - **302 Found (bei erfolgreicher Authentifizierung):** Leitet den Benutzer zur angegebenen Umleitungs-URL mit dem Authorization Code und/oder ID Token weiter.
  - **Beispiel Response (Redirect)** *noch nicht geprüft*

    ```http
    HTTP/1.1 302 Found
    Location: https://client.example.com/callback?code=SplxlOBeZQQYbYS6WxSbIA&state=xyzABC123
    ```

  - **400 Bad Request (Fehlende oder ungültige Parameter.)**
  - **Beispiel Response (Bad Request)** *noch nicht geprüft*

    ```http
    HTTP/1.1 400 Bad Request
    Content-Type: application/json
    {
      "error": "invalid_request",
      "error_description": "Missing required parameter: redirect_uri"
    }
    ```
 
  - **401 Unauthorized:** Ungültige oder fehlende Authentifizierung.
  - **500 Internal Server Error:** Serverfehler.

### 3. Token Endpoint

**Pfad:** `/token`

- **Beschreibung:** Ermöglicht den Tausch eines Refresh-Tokens gegen ein neues Access- und Refresh-Token. Unterstützt auch Client Assertion JWTs und DPoP.
- **Methoden:** `POST`
- **Anfragetypen:** `application/x-www-form-urlencoded`
- **Erforderliche Parameter:**
  - **grant_type (string, erforderlich):** Der Typ des Antrags, hier `refresh_token`. ([RFC 6749, Abschnitt 6](https://datatracker.ietf.org/doc/html/rfc6749#section-6))
  - **refresh_token (string, erforderlich):** Das aktuelle Refresh-Token, das getauscht werden soll. ([RFC 6749, Abschnitt 6](https://datatracker.ietf.org/doc/html/rfc6749#section-6))
  - **client_assertion (string, optional):** JWT, das den Client für die Anfrage authentifiziert. ([RFC 7523, Abschnitt 2.2](https://datatracker.ietf.org/doc/html/rfc7523#section-2.2))
  - **client_assertion_type (string, optional):** Der Typ des JWT-Assertions, in der Regel `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`. ([RFC 7523, Abschnitt 2.2](https://datatracker.ietf.org/doc/html/rfc7523#section-2.2))
  - **dpop (string, optional):** DPoP-Proof JWT, das die Bindung eines Tokens an ein spezifisches HTTP-Anforderungsobjekt beweist. ([DPoP Entwurf](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-dpop))

- **Antworten:**
  - **200 OK:**
    - **Content-Type:** `application/json`
    - **Beschreibung:** Gibt ein neues Access- und Refresh-Token zurück.
  - **400 Bad Request:** Ungültige Anfrageparameter.
  - **401 Unauthorized:** Ungültige oder fehlende Authentifizierung.

### 4. JWKS Endpoint

**Pfad:** `/jwks`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage der öffentlichen Signaturschlüssel, die vom Authorization Server verwendet werden, um Tokens zu signieren.
- **Methoden:** `GET`
- **Antworten:**
  - **200 OK**
    - **Content-Type:** `application/json`
    - **Beschreibung:** Liefert die JSON Web Key Set (JWKS) Datei mit den Signatur-Zertifikaten des Servers.
    - **Relevanter RFC:** [RFC 7517 - JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517)

### 5. Nonce Endpoint

**Pfad:** `/nonce`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Abfrage einer neuen Nonce, die für sicherheitsrelevante Transaktionen genutzt werden kann.
- **Methoden:** `GET`
- **Antworten:**
  - **200 OK**
    - **Content-Type:** `application/json`
    - **Beschreibung:** Gibt eine neue Nonce zurück.

### 6. Client Registration Endpoint

**Pfad:** `/clientreg`

- **Beschreibung:** Dieser Endpunkt ermöglicht die Registrierung von Clients mit verschiedenen Verfahren, die eine sichere Authentifizierung garantieren.
- **Methoden:** `POST`
- **Unterstützte Verfahren:**
  - **Android Key ID Attestation (für Google-Android Geräte)**
  - **Apple DCAppAttest**
  - **Signiertes Client Assertion JWT**
    - **Relevanter RFC:** [RFC 7523 - JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants](https://datatracker.ietf.org/doc/html/rfc7523)
  - **TPM signiertes Client Assertion JWT**
  - **ClientZertifikat plus Client Assertion JWT** (Nur für Dienst-zu-Dienst Kommunikation)
    - **Relevanter RFC:** [RFC 8705 - OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens](https://datatracker.ietf.org/doc/html/rfc8705)

- **Antworten:**
  - **201 Created:** Der Client wurde erfolgreich registriert.
  - **400 Bad Request:** Ungültige Registrierungsdaten oder Parameter.
  - **401 Unauthorized:** Ungültige oder fehlende Authentifizierung.
  - **500 Internal Server Error:** Serverfehler.

## Lizenz und Support

Für Fragen und Unterstützung wenden Sie sich bitte an das zuständige Team des Authorization Servers.
