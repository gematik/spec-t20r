# ZETA Guard - Client Registration and OAuth 2.0 Authorization Code Flow

Das folgende Diagramm beschreibt den **Client Registrierungs- und OAuth 2.0 Authorization Code Flow** mit den Erweiterungen **PAR (Pushed Authorization Requests)**, **PKCE (Proof Key for Code Exchange)** und **DPoP (Demonstration of Proof of Possession)**.

Die Client Registrierung erfolgt unter Einbeziehung von **Client Attestation** und **E-Mail-Verifizierung**. Diese Prozesse sind wichtig, um die Integrität des Clients und die Identität des Benutzers zu bestätigen.
Die Client Attestation stellt sicher, dass der Client in einer vertrauenswürdigen Umgebung ausgeführt wird, während die E-Mail-Verifizierung sicherstellt, dass der Benutzer tatsächlich Zugriff auf die angegebene E-Mail-Adresse hat. Die E-Mail-Verifizierung kann entfallen, wenn bereits bei einem anderen ZETA Guard Authorization Server eine erfolgreiche Verifizierung stattgefunden hat und das .
Die OAuth 2.0 Authorization Code Flow mit PKCE und DPoP bietet zusätzliche Sicherheit, indem sie den Austausch von Autorisierungscodes und Tokens absichert und sicherstellt, dass nur der berechtigte Client auf geschützte Ressourcen zugreifen kann.

![Client Registration and OAuth 2.0 Authorization Code Flow](/images/native-client-attestation-oidc-and-oauth.svg)

Das Diagramm beschreibt **zwei Hauptprozesse**:

1. Die **Client-Registrierung** unter Einbeziehung von Client Attestation und E-Mail-Verifizierung.
2. Den **OAuth 2.0 Authorization Code Flow** erweitert um PAR (Pushed Authorization Requests), PKCE (Proof Key for Code Exchange) und DPoP (Demonstration of Proof of Possession).

An den Prozessen sind verschiedene **Akteure und Systeme** beteiligt:

* **Aktor:** User.
* **Mobile Device Box:**
  * User Agent
  * Mail User Agent (MUA)
  * Client
  * Android TEE (Trusted Execution Environment)
  * Authenticator
* **Anbieter Box:**
  * **ZETA Guard Box:**
    * PDP (AuthS/Authorization Server und Policy Engine)
    * PEP (PEP HTTP Proxy)
  * **TI 2.0 Dienst Box:**
    * RS (Resource Server)
* **Externe Systeme:**
  * Attestation Service
  * IDP (Identity Provider)
  * Federation Master

---

## Ablauf 1: Client Registrierung (mit Client Attestation und E-Mail)

Dieser Abschnitt beschreibt den Prozess, bei dem sich ein Client-Gerät registriert und seine Identität sowie die Integrität der Umgebung durch Attestierung und ggf. E-Mail-Verifizierung bestätigt werden.

* Der User startet die Registrierung über den Client.
* Der Client generiert ein Schlüsselpaar für die Attestierung, wahlweise unter Verwendung des Android TEE oder der iOS Secure Enclave.
* Der Android TEE sendet den öffentlichen Schlüssel an den Client.
* Der Client fordert eine Attestation Challenge vom Attestation Service an.
* Der Attestation Service sendet die Attestation Challenge an den Client.
* Der Client signiert die Challenge mit dem Attestation-Schlüssel unter Verwendung des Android TEE (oder der iOS SafetyNet/Play Integrity bzw. DeviceCheck/App Attest APIs).
* Der Android TEE sendet das Attestation Statement an den Client.
* Der Client sendet die Client Registration Request an AuthS. Diese Anfrage enthält das Attestation Statement, den öffentlichen Schlüssel, die Benutzer-E-Mail und ein Software-Statement.
* AuthS verifiziert die Client Attestation über den Attestation Service. Hierbei leitet AuthS die Attestierungsdaten an den Attestation Service weiter.
* Der Attestation Service validiert das Attestation Statement.
* Der Attestation Service sendet das Attestation Verification Result an AuthS.
* AuthS verifiziert das E-Mail Confirmation JWT.
* Alternativer Ablauf: E-Mail Bestätigung erforderlich:
  * AuthS generiert einen Bestätigungslink und sendet eine E-Mail über das MUA.
  * Der User erhält die E-Mail.
  * Der User klickt auf den Bestätigungslink in der E-Mail.
  * Das MUA öffnet den Bestätigungslink im User Agent.
  * Der User Agent sendet die E-Mail Confirmation Request an AuthS.
  * AuthS verifiziert die E-Mail Confirmation Request.
  * AuthS generiert ein E-Mail Confirmation JWT mit spezifischen Claims (iss, sub, aud, exp, iat, Email_verified).
  * PDP evaluiert die Policy basierend auf den Eingangsdaten.
  * AuthS sendet die Client Registration Response (client_id, E-Mail Confirmation JWT) an den Client.
* Alternativer Ablauf: E-Mail Bestätigung bereits erfolgt:
  * PDP evaluiert die Policy basierend auf den Eingangsdaten.
  * AuthS sendet die Client Registration Response (client_id) an den Client.

---

## Ablauf 2: OAuth 2.0 Authorization Code Flow mit PAR, PKCE und DPoP

Dieser Abschnitt beschreibt den Prozess, bei dem der Client nach erfolgreicher Registrierung einen Access Token erhält, um auf geschützte Ressourcen zuzugreifen.

* Der Client generiert einen PKCE Code Verifier und einen PKCE Code Challenge.
* Der Client generiert ein DPoP Key Pair.
* Der Client sendet eine PAR Request (Pushed Authorization Request) an AuthS, inklusive client_id, redirect_uri, scope, etc., und dpop_jkt. Die Anfrage enthält auch DPoP Proof, code_challenge und code_challenge_method.
* AuthS validiert den DPoP Proof.
* AuthS sendet eine Request URI an den Client.
* Der Client navigiert den User Agent zur Request URI.
* Der User Agent sendet die Authorization Request (mit Request URI) an AuthS.
* Gruppe: OIDC User Authentifizierung mit confidential client:
  * AuthS agiert als Relying Party für das IDP.
  * AuthS sendet eine PAR Request (OpenID Connect) an das IDP.
  * Das IDP sendet eine URI-PAR Response (request_uri, expires_in) an AuthS.
  * AuthS leitet die URI-PAR an den Client weiter.
  * Der Client leitet die URI-PAR an den Authenticator weiter.
  * Der Authenticator navigiert zum URI-PAR beim IDP.
  * Das IDP sendet den Authentication Prompt und Consent an den Authenticator.
  * Der Authenticator sendet User Credentials und Consent an das IDP.
  * Das IDP leitet den Authenticator mit auth_code und redirect_uri an AuthS weiter.
  * Der Authenticator leitet den Client mit auth_code und redirect_uri an AuthS weiter.
  * Der Client leitet mit auth_code und redirect_uri an AuthS weiter.
  * AuthS sendet eine Token Request (Authorization Code Grant) an das IDP.
  * Das IDP validiert den Authorization Code.
  * Das IDP sendet die Authentication Response (ID Token) an AuthS.
* AuthS validiert das ID Token.
* AuthS sendet den Authorization Code an den User Agent.
* Der User Agent leitet den Client mit dem Authorization Code weiter.
* Der Client generiert ein DPoP Proof JWT.
* Der Client sendet eine Token Request (Authorization Code Grant) an AuthS. Diese enthält den Authorization Code, DPoP Proof, client_id, redirect_uri und code_verifier.
* AuthS validiert den Authorization Code.
* AuthS validiert den DPoP Proof.
* AuthS validiert den PKCE Code Verifier.
* PDP evaluiert die Policy basierend auf den Eingangsdaten.
* AuthS sendet Access Token und Refresh Token an den Client. Der Access Token ist dabei an den DPoP Public Key des Clients gebunden.
* Der Client generiert einen DPoP Token.
* Der Client greift über PEP auf eine geschützte Ressource zu, unter Verwendung des Access Tokens und des DPoP Proofs.
* PEP validiert den Access Token und den DPoP Proof.
* PEP leitet die Anfrage an den Resource Server A (RS) weiter.
* Der RS sendet Resource Data an PEP.
* PEP sendet Resource Data an den Client.
