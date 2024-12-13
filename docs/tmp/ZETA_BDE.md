# ZETA BDE - Betriebsdatenerfassung

## Beschreibung der zu erfassenden Daten und deren Zweck

Die Erfassung der Betriebsdaten dient sowohl der **Betriebsüberwachung** als auch der **Sicherheitsanalyse**. Dabei soll sichergestellt werden, dass Datenschutzvorgaben eingehalten werden und die Erhebung auf ein Minimum beschränkt wird, das für die genannten Zwecke erforderlich ist. Die zu erfassenden Daten sind nach Komponenten und Verwendungszweck aufgeteilt:

---

### **HTTP Request-Daten**
1. **Komponenten**
   - PEP
   - PDP
     - Auth Server
     - Client-Registry
     - Policy Engine
   - Notification Service
   - Cluster Management Service
2. **Zweck**:
   - **Betriebsüberwachung**: Identifikation von Bottlenecks, Fehlkonfigurationen und Auswertungen der Lastverteilung.
   - **Sicherheitsanalyse**: Erkennung unautorisierter Zugriffe, Anomalien und potenzieller Angriffe.
3. **Erfasste Attribute**:
   - **Method**: Analyse der genutzten HTTP-Methoden.
   - **URL**: Optional, konfigurierbar (z. B. ob Parameter eingeschlossen werden), zur Analyse angefragter Ressourcen.
   - **Host**: Identifikation der Zielkomponenten.
   - **User-Agent**: Erkennung von Clients und Analyse verdächtiger Client-Muster.
   - **Referer**: Verfolgung der Ursprungsquelle des Requests.
   - **Accept**: Analyse der erwarteten Antworttypen.
   - **Authorization**: Nur das Format (z. B. "Bearer").
   - **Cookie**: Nur die Namen, keine Inhalte (zur Analyse, welche Cookies verwendet werden).
   - **Zeitstempel Request Eingang**: Zeitbasierte Analyse und Korrelation von Ereignissen.
   - **Custom-Header**: Konfigurierbar zur Erfassung spezifischer zusätzlicher Informationen.
   - **User-Daten**: Nur `professionOID`, sofern datenschutzkonform.
   - **Client-Daten**: Nur `clientID`, sofern datenschutzkonform.
   - **PoPP-Daten**: Nur ob vorhanden, ggf. bestimmte Attribute (z. B. `iat` oder `proofMethod`).
   - **IP-Adresse**: Optional, abhängig von Datenschutzprüfung.
   - **Request size**: Analyse der Datenvolumen.

---

### **HTTP Response-Daten**
1. **Zweck**:
   - **Betriebsüberwachung**: Nachvollziehbarkeit der Antworten, Status-Codes und deren Häufigkeit.
   - **Sicherheitsanalyse**: Analyse auffälliger Antwortmuster (z. B. gehäufte 500er-Statuscodes).
2. **Erfasste Attribute**:
   - **Status-Code**: Erfolg oder Fehleranalyse.
   - **Content-Type**: Identifikation von Datentypen in der Antwort.
   - **Content-Length**: Bewertung der Antwortgröße.
   - **Set-Cookie**: Nur Namen, zur Identifikation von Cookie-Nutzungen.
   - **Location**: Optional, ob Weiterleitungen erfolgen und wohin.
   - **Zeitstempel Response Ausgang**: Zeitbasierte Korrelation mit Request-Daten.
   - **Response size**: Bewertung des Datenflusses.
   - **Custom-Header**: Konfigurierbar, keine sensiblen Inhalte.

---

### **Client-Registrierung**
1. **Zweck**:
   - **Betriebsüberwachung**: Nachvollziehbarkeit von Registrierungsvorgängen.
   - **Sicherheitsanalyse**: Überwachung und Identifikation unautorisierter Registrierungsversuche.
2. **Erfasste Attribute**:
   - **ClientID**: Eindeutige Identifikation des registrierten Clients.
   - **OPS ProductID, Version, OS**: Analyse der genutzten Softwareumgebungen.
   - **Zeitstempel**: Historisierung der Ereignisse.

---

### **Policy Decision (PDP)**
1. **Zweck**:
   - **Sicherheitsanalyse**: Nachvollziehbarkeit von Policy-Entscheidungen.
2. **Erfasste Attribute**:
   - **IP-Adresse**: Optional, zur Zuordnung von Anfragen.
   - **Zeitstempel**: Historisierung und Korrelation.
   - **Zweite Policy Engine**: Optional, zur Analyse von Policy-Entscheidungen.

---

### **SIEM Alerts**
1. **Zweck**:
   - **Sicherheitsanalyse**: Identifikation von sicherheitsrelevanten Ereignissen.
2. **Erfasste Attribute**:
   - **Alert-Daten**: Abhängig von der Struktur des SIEM-Systems (z. B. ID, Typ, Beschreibung).
   - **Zeitstempel**: Historisierung.

---

### **Notification Management**
1. **Zweck**:
   - **Betriebsüberwachung**: Nachvollziehbarkeit von Notification Konfiguration und Versand.
2. **Erfasste Attribute**:
   - **Notification-Daten**: noch offen (z. B. Verwaltung der Notification Konfiguration, Versendete Notification-Events).
   - **Zeitstempel**: Historisierung.

---

## Datenformat und Transport

1. **Datenformat**:
   - **JSON**: Alle Daten werden in JSON-Objekten erfasst, die durch Schemadateien validiert werden können. Das Format erlaubt:
     - Eindeutige Struktur der Daten.
     - Erweiterbarkeit durch zusätzliche Attribute (`additionalProperties: true`).
     - Unterstützung von Verschachtelungen (z. B. HTTP Header innerhalb von Requests).

2. **Transport**:
   - **Protokoll**: Sicherer Transport über HTTPS mit TLS 1.2 oder höher.
   - **Authentifizierung**: Zugriff auf den BDE-Server nur durch autorisierte Komponenten, z. B. mit OAuth2 Client-Zertifikaten.
   - **Batch-Verarbeitung**: Daten können periodisch gesammelt und gebündelt an den Server gesendet werden, um die Netzwerkbelastung zu minimieren.

---

---

## Offene Punkte

- Soll auch ZETA Guard interne Kommunikation für BDE aufbereitet werden? Policy Decision ja; Zugriff auf DBs noch nicht geklärt.
- Es soll auch Kommunikation von Moonitoring und SIEM des Anbieters zu ZETA Guard Komponenten für BDE aufbereitet werden
- Es sollen Daten vom Cluster Management Service zum Zustand des Clusters an BDE geliefert werden (start und stop von Pods z. B.)

---

## Anforderungen an den BDE-Server

1. **Validierung**:
   - Muss JSON-Datenstrukturen gemäß bereitgestellter Schemata verarbeiten.
   - Flexible Validierung durch Unterstützung von `additionalProperties: true`.

2. **Leistung**:
   - Verarbeitung großer Datenmengen in Echtzeit oder asynchron.
   - Skalierbarkeit, um Lastspitzen bei vielen eingehenden Daten zu bewältigen.

3. **Sicherheit**:
   - Authentifizierte und verschlüsselte Kommunikation.
   - Zugriffskontrollen für empfangene Daten.

4. **Speicherung und Auswertung**:
   - Speicherung von Betriebs- und Sicherheitsdaten für definierte Retentionszeiten.
   - Unterstützung von Abfragen zur Analyse der Betriebs- und Sicherheitsmetriken.