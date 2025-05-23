# Zero Trust API

![gematik logo](/images/gematik_logo.svg)

Eine gute API-Dokumentation sollte umfassend und klar strukturiert sein, um Entwicklern die Nutzung der API so einfach wie möglich zu machen. Hier sind die wichtigsten Elemente, die eine gute API-Dokumentation enthalten sollte:

## 1.1. Einführung

Zweck der API: Eine kurze Erklärung, was die API tut und welche Probleme sie löst.
Zielgruppe: Wer sollte diese API nutzen? Welche technischen Vorkenntnisse werden erwartet?
Voraussetzungen: Informationen über benötigte Tools, Bibliotheken oder SDKs.

## 1.2. Inhalt

- [Zero Trust API](#zero-trust-api)
  - [1.1. Einführung](#11-einführung)
  - [1.2. Inhalt](#12-inhalt)
  - [1.3. Authentifizierung und Autorisierung](#13-authentifizierung-und-autorisierung)
  - [1.4. Basis-URL und Endpunkte](#14-basis-url-und-endpunkte)
    - [1.4.1. Beispielanfragen und -antworten](#141-beispielanfragen-und--antworten)
    - [1.4.2. Antworten und Statuscodes](#142-antworten-und-statuscodes)
    - [1.4.3. Datenstrukturen und Modelle](#143-datenstrukturen-und-modelle)
    - [1.4.4. Rate Limits und Einschränkungen](#144-rate-limits-und-einschränkungen)
  - [1.5. Versionierung](#15-versionierung)
  - [1.6. Support und Kontaktinformationen](#16-support-und-kontaktinformationen)
  - [1.7. FAQs und Troubleshooting](#17-faqs-und-troubleshooting)
  - [1.8. Interaktive Dokumentation (optional)](#18-interaktive-dokumentation-optional)
  - [1.9. Changelog](#19-changelog)
  - [1.10. git Branch Modell](#110-git-branch-modell)
  - [1.11. Lizenzbedingungen](#111-lizenzbedingungen)


## 1.3. Authentifizierung und Autorisierung

Wie können Entwickler sich authentifizieren und welche Berechtigungen gibt es?
Welche Sicherheitsmaßnahmen sind getroffen?

API-Schlüssel oder Token: Wie erhält der Nutzer einen API-Schlüssel oder ein Authentifizierungstoken?
Autorisierungsverfahren: Beschreibung der verwendeten Authentifizierungsmethoden (z.B. OAuth, Basic Auth).
Beispiele: Beispielanfragen für die Authentifizierung.

## 1.4. Basis-URL und Endpunkte

Basis-URL: Die grundlegende URL, von der alle API-Aufrufe ausgehen.
Endpunkte: Detaillierte Beschreibung aller verfügbaren Endpunkte, einschließlich:
HTTP-Methode: GET, POST, PUT, DELETE, etc.
Pfadparameter: Parameter, die in der URL enthalten sind.
Query-Parameter: Parameter, die in der URL als Abfrage angehängt werden.
Body-Parameter: Parameter, die im Body einer Anfrage gesendet werden.
Mögliche Antwortformate (JSON, XML)

### 1.4.1. Beispielanfragen und -antworten

Codebeispiele: Beispielcode in verschiedenen Programmiersprachen (z.B. Python, JavaScript, Curl), um die API-Aufrufe zu demonstrieren.
Erwartete Antworten: Darstellung der typischen API-Antworten für die gegebenen Anfragen.

### 1.4.2. Antworten und Statuscodes

Beispielantworten: JSON-, XML- oder andere Formatbeispiele der API-Antworten.
Statuscodes: Liste der möglichen HTTP-Statuscodes mit Erklärungen (z.B. 200 OK, 404 Not Found, 500 Internal Server Error).
Fehlermeldungen: Beschreibung der möglichen Fehler und wie sie zu beheben sind.

### 1.4.3. Datenstrukturen und Modelle

Datenformate: Erklärung der verwendeten Datenformate (z.B. JSON, XML).
Datenmodelle: Beschreibung der verwendeten Datenmodelle, inklusive aller Felder und Datentypen.
Beziehungen: Erklärung von Beziehungen zwischen verschiedenen Datenmodellen, falls zutreffend.

### 1.4.4. Rate Limits und Einschränkungen

Rate Limits: Informationen über die Anzahl der erlaubten Anfragen pro Zeiteinheit.
Nutzungseinschränkungen: Informationen über eventuelle Einschränkungen der API-Nutzung, wie z.B. die maximale Größe von Anfragen.

## 1.5. Versionierung

API-Versionierung: Hinweise darauf, wie Versionen der API verwaltet werden und wie Benutzer zwischen verschiedenen Versionen wechseln können.
Änderungsprotokoll: Ein Changelog, das alle wichtigen Änderungen und Updates dokumentiert.

## 1.6. Support und Kontaktinformationen

Hilfe: Informationen darüber, wo und wie Benutzer Unterstützung erhalten können (z.B. Forum, E-Mail-Support).
Fehlerberichterstattung: Wie können Nutzer Bugs melden oder Feature-Anfragen stellen?

## 1.7. FAQs und Troubleshooting

Häufige Fragen: Antworten auf häufige Fragen zur Nutzung der API.
Fehlerbehebung: Leitfaden zur Behebung häufiger Probleme.

## 1.8. Interaktive Dokumentation (optional)

Swagger/OpenAPI: Ein interaktives Interface, mit dem Entwickler API-Endpunkte direkt aus der Dokumentation heraus testen können.
API-Sandbox: Eine Testumgebung, in der Entwickler sicher mit der API experimentieren können.
Eine gut strukturierte API-Dokumentation erleichtert es Entwicklern, die API effizient zu nutzen, und trägt dazu bei, häufige Fragen und Probleme zu minimieren.

## 1.9. Changelog

Ein detaillierter Verlauf der Änderungen an der API.

## 1.10. git Branch Modell

In diesem Repository werden Branches verwendet um den Status der Weiterentwicklung und das Review von Änderungen abzubilden.

Folgende Branches werden verwendet

- *main* (enthält den letzten freigegebenen Stand der Entwicklung; besteht permanent)
- *develop* (enthält den Stand der fertig entwickelten Features und wird zum Review durch Industriepartner und Gesellschafter verwendet; basiert auf main; nach Freigabe erfolgt ein merge in main und ein Release wird erzeugt; besteht permanent)
- *feature/[name]* (in feature branches werden neue Features entwickelt; basiert auf develop; nach Fertigstellung erfolgt ein merge in develop; wird nach dem merge gelöscht)
- *hotfix/[name]* (in hotfix branches werden Hotfixes entwickelt; basiert auf main; nach Fertigstellung erfolgt ein merge in develop und in main; wird nach dem merge gelöscht)
- *concept/[name]* (in feature branches werden neue Konzepte entwickelt; basiert auf develop; dient der Abstimmung mit Dritten; es erfolgt kein merge; wird nach Bedarf gelöscht)
- *misc/[name]* (nur für internen Gebrauch der gematik; es erfolgt kein merge; wird nach Bedarf gelöscht)

## 1.11. Lizenzbedingungen

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
