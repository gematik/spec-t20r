### Überblick über die Zero Trust Architektur und deren Hauptkomponenten

**1. Hauptkomponenten:**
   - **PEP (Policy Enforcement Point)**: Ein HTTP-Proxy, der die Zugriffe auf Ressourcen durch Token-Validierung kontrolliert.
   - **PDP (Policy Decision Point)**: Ein OAuth 2.0 Authorization Server, bestehend aus:
     - **Authorization Server**: Stellt Access- und Refresh-Tokens aus.
     - **Client Registry**: Speichert Client-bezogene Informationen.
     - **Policy Engine**: Entscheidet über die Zugriffsbefugnisse anhand der Richtlinien.

**2. Speicherung und Datenstrukturen in einer Key/Value-Datenbank:**
   - Speichert Informationen zu **Sessions**, **Usern**, **Clients** und **Tokens**.
   - Jedes Token, jede Session und jeder registrierte Client hat eine spezifische Struktur, die zur Authentifizierung, Autorisierung und Policy Enforcement dient.

---

### Beschreibung der Datenstrukturen und deren Nutzung

**1. AccessToken**  
   - **Beschreibung**: Enthält Berechtigungsinformationen für den Client zur Nutzung geschützter Ressourcen.
   - **Verwendung**: Wird im PEP bei Anfragen an geschützte Endpunkte überprüft.
   - **Wichtige Felder**:
     - `jti`: JWT ID zur eindeutigen Identifikation des Tokens.
     - `iss`: Der Aussteller, hier der PDP Authorization Server.
     - `exp`: Ablaufzeitpunkt des Tokens (Unix-Timestamp).
     - `cnf`: Enthält `jkt` zur Bindung an einen öffentlichen Schlüssel (DPoP).
   - **Prozess im PEP**: Die `jti` wird genutzt, um zugehörige User- und Client-Informationen abzurufen.

**2. RefreshToken**  
   - **Beschreibung**: Dient zur Erneuerung des AccessTokens, wenn dieses abgelaufen ist.
   - **Verwendung**: Wird vom Authorization Server ausgegeben und bei Anfragen zur Token-Erneuerung verwendet.
   - **Wichtige Felder**:
     - `jti`: Zur Identifikation des Tokens.
     - `iss`, `exp`, `iat`: Wie bei AccessToken.
     - `cnf`: Bestätigung zur Bindung an den öffentlichen Schlüssel (`jkt`).

**3. UserSession**  
   - **Beschreibung**: Repräsentiert den Sitzungsstatus eines authentifizierten Users.
   - **Verwendung**: Wird vom Authorization Server angelegt und aktualisiert, wenn sich ein User authentifiziert.
   - **Wichtige Felder**:
     - `session_id`: Eindeutige ID für die Session.
     - `subject`: ID des authentifizierten Users.
     - `client_id`: ID des zugreifenden Clients.
     - `session_expiry`: Ablaufzeit der Session.
     - `refresh_count`: Zähler, wie oft ein RefreshToken verwendet wurde.

**4. UserInfo**  
   - **Beschreibung**: Enthält benutzerspezifische Informationen, wie Identifikatoren und Berufsinformationen.
   - **Verwendung**: Kann vom PEP abgerufen werden, um User-spezifische Daten in Anfragen an den Resource Server einzubinden.
   - **Wichtige Felder**:
     - `subject`: Benutzer-ID, vergeben vom Authorization Server.
     - `identifier`: Eindeutiger Benutzer-Identifikator (z.B. KVNR).
     - `professionOID`: Berufskodierung (OID).

**5. ClientInstance**  
   - **Beschreibung**: Speichert die Registrierungsinformationen des Clients.
   - **Verwendung**: Wird vom Authorization Server bei der Client-Registrierung gespeichert und beim Zugriff auf Ressourcen verwendet.
   - **Wichtige Felder**:
     - `client_id`: ID des Clients.
     - `product_id`, `manufacturer_id`: Identifikatoren für das Client-Produkt und den Hersteller.
     - `owner`: Eigentümer des Clients.

---

### Prozessabläufe und Interaktionen

**1. Authentifizierung des Users am Authorization Server**
   - Der User authentifiziert sich am Authorization Server.
   - Bei erfolgreicher Authentifizierung werden folgende Einträge in der Datenbank angelegt:
     - **UserSession**-Eintrag: Repräsentiert die aktive Sitzung des Users.
     - **UserInfo**-Eintrag: Speichert benutzerspezifische Daten wie `identifier` und `professionOID`.
   - Der Authorization Server stellt Access- und Refresh-Tokens für den Client aus.

**2. Registrierung eines Clients**
   - Der Client registriert sich am Authorization Server und erhält einen **ClientInstance**-Eintrag.
   - **ClientInstance** speichert Informationen wie `product_id`, `manufacturer_id`, `owner` und weitere Details zur Plattform und Sicherheitslage (Posture, Attestation).

**3. Nutzung des AccessTokens am PEP zur Ressourcenzugriffskontrolle**
   - Der Client verwendet das AccessToken, um einen geschützten Endpunkt des Resource Servers aufzurufen.
   - Der PEP (HTTP-Proxy) überprüft das AccessToken:
     - Über die `jti` des Tokens werden **UserInfo** und **ClientInstance**-Einträge aus der Datenbank geladen.
     - Diese Informationen werden als zusätzliche HTTP-Header in die Anfrage eingefügt:
       - **User-Informationen**: Enthält `identifier` und `professionOID`.
       - **Client-Informationen**: Details wie `product_id`, `manufacturer_id`, und `platform`.
   - Die angereicherte Anfrage wird an den Resource Server weitergeleitet, der dann eine Zugriffskontrolle anhand der zusätzlichen Informationen durchführen kann.

---

### Wichtige Punkte für die Implementierung

1. **Token Validierung im PEP**: Implementieren Sie eine Token-Validierung im PEP, die das AccessToken prüft und anhand von `jti` verknüpfte Daten abruft.
2. **Datenbankabfragen für erweiterte Header**: Konfigurieren Sie den PEP so, dass er die verknüpften **UserInfo** und **ClientInstance**-Einträge als Header hinzufügt, bevor eine Anfrage an den Resource Server geleitet wird.
3. **Speicherung und Erneuerung von Sitzungen**: Der PDP Authorization Server muss den Sitzungsstatus pflegen und das **UserSession**-Objekt entsprechend aktualisieren.
4. **Verwaltung von Access und Refresh Tokens**: Achten Sie darauf, dass die Tokens korrekt generiert und nach Ablauf automatisch durch den PDP Authorization Server erneuert werden.
5. **Sicherheitsüberprüfungen**: Verwenden Sie die `cnf`-Informationen (insbesondere `jkt`) im Token zur Bestätigung der Bindung an einen öffentlichen Schlüssel, um die Sicherheit gegen Token-Diebstahl zu gewährleisten.

