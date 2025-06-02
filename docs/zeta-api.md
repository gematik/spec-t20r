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
  - [1.4. Authentifizierung und Autorisierung](#14-authentifizierung-und-autorisierung)
  - [1.5. Endpunkte](#15-endpunkte)
    - [1.5.1 ZETA Guard API Endpunkte](#151-zeta-guard-api-endpunkte)
      - [1.5.1.1 OAuth Protected Resource Well-Known Endpoint](#1511-oauth-protected-resource-well-known-endpoint)
        - [1.5.1.1.1 Basis-URL](#15111-basis-url)
        - [1.5.1.1.2 Beispielanfragen und -antworten](#15112-beispielanfragen-und--antworten)
        - [1.5.1.2.3 Antworten und Statuscodes](#15123-antworten-und-statuscodes)
        - [1.5.1.3.4 Datenstrukturen und Modelle](#15134-datenstrukturen-und-modelle)
        - [1.5.1.4.5 Rate Limits und Einschränkungen](#15145-rate-limits-und-einschränkungen)
      - [1.5.1.2 Authorization Server Well-Known Endpoint](#1512-authorization-server-well-known-endpoint)
        - [1.5.1.2.1 Basis-URL](#15121-basis-url)
        - [1.5.1.2.2 Beispielanfragen und -antworten](#15122-beispielanfragen-und--antworten)
        - [1.5.1.2.3 Antworten und Statuscodes](#15123-antworten-und-statuscodes-1)
        - [1.5.1.3.4 Datenstrukturen und Modelle](#15134-datenstrukturen-und-modelle-1)
        - [1.5.1.4.5 Rate Limits und Einschränkungen](#15145-rate-limits-und-einschränkungen-1)
      - [1.5.1.3 Nonce Endpoint](#1513-nonce-endpoint)
        - [1.5.1.3.1 Basis-URL](#15131-basis-url)
        - [1.5.1.3.2 Beispielanfragen und -antworten](#15132-beispielanfragen-und--antworten)
        - [1.5.1.3.3 Antworten und Statuscodes](#15133-antworten-und-statuscodes)
        - [1.5.1.3.4 Datenstrukturen und Modelle](#15134-datenstrukturen-und-modelle-2)
        - [1.5.1.3.5 Rate Limits und Einschränkungen](#15135-rate-limits-und-einschränkungen)
      - [1.5.1.4 Dynamic Client Registration Endpoint](#1514-dynamic-client-registration-endpoint)
        - [1.5.1.4.1 Basis-URL](#15141-basis-url)
        - [1.5.1.4.2 Beispielanfragen und -antworten](#15142-beispielanfragen-und--antworten)
        - [1.5.1.4.3 Antworten und Statuscodes](#15143-antworten-und-statuscodes)
        - [1.5.1.4.4 Datenstrukturen und Modelle](#15144-datenstrukturen-und-modelle)
        - [1.5.1.4.5 Rate Limits und Einschränkungen](#15145-rate-limits-und-einschränkungen-2)
      - [1.5.1.5 Token Endpoint](#1515-token-endpoint)
        - [1.5.1.5.1 Basis-URL](#15151-basis-url)
        - [1.5.1.5.2 Beispielanfragen und -antworten](#15152-beispielanfragen-und--antworten)
        - [1.5.1.5.3 Antworten und Statuscodes](#15153-antworten-und-statuscodes)
        - [1.5.1.5.4 Datenstrukturen und Modelle](#15154-datenstrukturen-und-modelle)
        - [1.5.1.5.5 Rate Limits und Einschränkungen](#15155-rate-limits-und-einschränkungen)
      - [1.5.1.6 Resource Endpoint](#1516-resource-endpoint)
        - [1.5.1.6.1 Basis-URL](#15161-basis-url)
        - [1.5.1.6.2 Beispielanfragen und -antworten](#15162-beispielanfragen-und--antworten)
        - [1.5.1.6.3 Antworten und Statuscodes](#15163-antworten-und-statuscodes)
        - [1.5.1.6.4 Datenstrukturen und Modelle](#15164-datenstrukturen-und-modelle)
        - [1.5.1.6.5 Rate Limits und Einschränkungen](#15165-rate-limits-und-einschränkungen)
    - [1.5.2 Konnektor/TI-Gateway Endpunkte](#152-konnektorti-gateway-endpunkte)
      - [1.5.2.1 getCertificate](#1521-getcertificate)
      - [1.5.2.1 externalAuthenticate](#1521-externalauthenticate)
    - [1.5.3 ZETA Attestation Service Endpunkte](#153-zeta-attestation-service-endpunkte)
      - [1.5.3.1 getAttestation](#1531-getattestation)
  - [1.6. Versionierung](#16-versionierung)
  - [1.7. Performance- und Lastannahmen](#17-performance--und-lastannahmen)
  - [1.8. Support und Kontaktinformationen](#18-support-und-kontaktinformationen)
  - [1.9. FAQs und Troubleshooting](#19-faqs-und-troubleshooting)
  - [1.10. Interaktive Dokumentation (optional)](#110-interaktive-dokumentation-optional)
  - [1.11. Changelog](#111-changelog)
  - [1.12. git Branch Modell](#112-git-branch-modell)
  - [1.13. Lizenzbedingungen](#113-lizenzbedingungen)

## 1.3 Voraussetzungen für die ZETA Client Nutzung

Der FQDN des Resource Servers wird vom ZETA Client benötigt, um die ZETA Guard API zu erreichen.

Für Anwendungsfälle in denen ein PoPP Token benötigt wird, muss das PoPP Token im Header PoPP an den ZETA Client übergeben werden.

Die roots.json Datei wird vom ZETA Client benötigt, um die Trust Chain zu validieren. Diese Datei muss regelmäßig aktualisiert werden.

## 1.4. Authentifizierung und Autorisierung

Wie können Entwickler sich authentifizieren und welche Berechtigungen gibt es?
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

#### 1.5.1.1 OAuth Protected Resource Well-Known Endpoint


##### 1.5.1.1.1 Basis-URL



##### 1.5.1.1.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.2.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.3.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.4.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.

#### 1.5.1.2 Authorization Server Well-Known Endpoint


##### 1.5.1.2.1 Basis-URL



##### 1.5.1.2.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.2.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.3.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.4.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.

#### 1.5.1.3 Nonce Endpoint


##### 1.5.1.3.1 Basis-URL



##### 1.5.1.3.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.3.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.3.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.3.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.


#### 1.5.1.4 Dynamic Client Registration Endpoint


##### 1.5.1.4.1 Basis-URL



##### 1.5.1.4.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.4.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.4.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.4.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.


#### 1.5.1.5 Token Endpoint


##### 1.5.1.5.1 Basis-URL



##### 1.5.1.5.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.5.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.5.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.5.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.


#### 1.5.1.6 Resource Endpoint


##### 1.5.1.6.1 Basis-URL



##### 1.5.1.6.2 Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

##### 1.5.1.6.3 Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

##### 1.5.1.6.4 Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

##### 1.5.1.6.5 Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.

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

## 1.8. Support und Kontaktinformationen

Hilfe: Informationen darüber, wo und wie Benutzer Unterstützung erhalten können (z.B. Forum, E-Mail-Support).
Fehlerberichterstattung: Wie können Nutzer Bugs melden oder Feature-Anfragen stellen?

## 1.9. FAQs und Troubleshooting

Häufige Fragen: Antworten auf häufige Fragen zur Nutzung der API.
Fehlerbehebung: Leitfaden zur Behebung häufiger Probleme.

## 1.10. Interaktive Dokumentation (optional)

Swagger/OpenAPI: Ein interaktives Interface, mit dem Entwickler API-Endpunkte direkt aus der Dokumentation heraus testen können.
API-Sandbox: Eine Testumgebung, in der Entwickler sicher mit der API experimentieren können.
Eine gut strukturierte API-Dokumentation erleichtert es Entwicklern, die API effizient zu nutzen, und trägt dazu bei, häufige Fragen und Probleme zu minimieren.

## 1.11. Changelog

Ein detaillierter Verlauf der Änderungen an der API.

## 1.12. git Branch Modell

In diesem Repository werden Branches verwendet um den Status der Weiterentwicklung und das Review von Änderungen abzubilden.

Folgende Branches werden verwendet

- *main* (enthält den letzten freigegebenen Stand der Entwicklung; besteht permanent)
- *develop* (enthält den Stand der fertig entwickelten Features und wird zum Review durch Industriepartner und Gesellschafter verwendet; basiert auf main; nach Freigabe erfolgt ein merge in main und ein Release wird erzeugt; besteht permanent)
- *feature/[name]* (in feature branches werden neue Features entwickelt; basiert auf develop; nach Fertigstellung erfolgt ein merge in develop; wird nach dem merge gelöscht)
- *hotfix/[name]* (in hotfix branches werden Hotfixes entwickelt; basiert auf main; nach Fertigstellung erfolgt ein merge in develop und in main; wird nach dem merge gelöscht)
- *concept/[name]* (in feature branches werden neue Konzepte entwickelt; basiert auf develop; dient der Abstimmung mit Dritten; es erfolgt kein merge; wird nach Bedarf gelöscht)
- *misc/[name]* (nur für internen Gebrauch der gematik; es erfolgt kein merge; wird nach Bedarf gelöscht)

## 1.13. Lizenzbedingungen

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
