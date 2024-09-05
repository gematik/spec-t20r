# Desktop Client für Versicherte

- im Wesentlichen, wie PS mit TPM
- Authentifizierung über das mobile Gerät des Versicherten
- Muss man Versicherte ohne Mobil-Gerät unterstützen? Ja, mit eGK


Die Authentifizierung für einen Desktop-Client, bei der sich der Nutzer über sein mobiles Gerät authentifizieren kann, kann durch die Integration mehrerer Technologien und Sicherheitsmethoden erreicht werden. Dieser Ansatz nutzt oft die Stärken von Multi-Faktor-Authentifizierung (MFA) und mobilen Authentifizierungslösungen. Hier ist ein detaillierter Überblick über den Ablauf und die Technologien, die typischerweise verwendet werden:

### 1. **Setup und Registrierung**

1. **Initiale Registrierung**:
   - Der Benutzer registriert sich zunächst auf dem Desktop-Client und/oder der Web-Anwendung. Dabei gibt er seine Identität an und verbindet sein mobiles Gerät mit dem Desktop-Client.
   - Dies kann durch Scannen eines QR-Codes, Eingeben eines Registrierungscodes oder über eine direkte Kopplung der Geräte geschehen.

2. **App-Installation**:
   - Der Benutzer installiert eine Authentifizierungs-App auf dem mobilen Gerät. Diese App könnte eine dedizierte Authentifizierungs-App (z.B. Google Authenticator, Microsoft Authenticator) oder eine spezielle App des Unternehmens sein.

### 2. **Authentifizierungsvorgang**

1. **Anmeldeversuch auf dem Desktop-Client**:
   - Der Benutzer versucht, sich auf dem Desktop-Client anzumelden. Der Client sendet eine Authentifizierungsanforderung an den Server, um den Anmeldevorgang zu starten.

2. **Challenge an das mobile Gerät**:
   - Der Server generiert eine Authentifizierungs-Challenge (z.B. einen Einmal-Code oder eine Push-Benachrichtigung) und sendet diese an das mobile Gerät des Benutzers.
   - Bei Verwendung einer Authentifizierungs-App kann dies ein Einmal-Passwort (OTP) oder ein Code sein, den der Benutzer in die App eingeben muss.
   - Bei Verwendung einer Push-Benachrichtigung erhält der Benutzer eine Nachricht auf seinem mobilen Gerät, die er zur Bestätigung oder Ablehnung der Anmeldeanforderung nutzen kann.

3. **Antwort vom mobilen Gerät**:
   - **Für OTPs**: Der Benutzer gibt das OTP, das von der Authentifizierungs-App generiert wurde, auf dem Desktop-Client ein.
   - **Für Push-Benachrichtigungen**: Der Benutzer akzeptiert oder lehnt die Anmeldeanforderung direkt in der Authentifizierungs-App auf dem mobilen Gerät ab.

4. **Verifizierung der Antwort**:
   - Der Server überprüft die vom mobilen Gerät erhaltene Antwort. Bei OTPs wird geprüft, ob der Code korrekt und innerhalb der gültigen Zeitspanne liegt.
   - Bei Push-Benachrichtigungen wird überprüft, ob die Genehmigung oder Ablehnung gültig ist.

5. **Zugriff gewähren oder verweigern**:
   - Wenn die Authentifizierung erfolgreich ist, gewährt der Server dem Desktop-Client Zugang. Andernfalls wird der Zugriff verweigert und der Benutzer wird ggf. aufgefordert, es erneut zu versuchen oder alternative Authentifizierungsmaßnahmen zu ergreifen.

### 3. **Zusätzliche Sicherheitsmaßnahmen**

1. **Biometrische Authentifizierung**:
   - Einige mobile Geräte unterstützen biometrische Authentifizierungsmethoden wie Fingerabdruck oder Gesichtserkennung. Diese können für zusätzliche Sicherheit bei der Bestätigung von Authentifizierungsanfragen genutzt werden.

2. **Gerätebindung**:
   - Der Server kann zusätzliche Sicherheitsprüfungen durchführen, um sicherzustellen, dass das mobile Gerät autorisiert und sicher ist. Dies kann durch Geräte-IDs, Zertifikate oder andere spezifische Merkmale geschehen.

3. **Verwendung von OAuth oder OpenID Connect**:
   - Diese Protokolle ermöglichen eine sichere Authentifizierung und Autorisierung, indem sie Token-basierte Systeme verwenden. Das mobile Gerät kann als Teil des Authentifizierungsflusses Token erzeugen oder verifizieren.

4. **Sicherheitsüberprüfung des mobilen Geräts**:
   - Vor der Authentifizierung kann überprüft werden, ob das mobile Gerät sicher ist (z. B. keine Root-Rechte oder Jailbreak). Diese Überprüfungen können zusätzliche Sicherheit bieten.

5. **Ereignisprotokollierung und Monitoring**:
   - Überwachung und Protokollierung der Authentifizierungsversuche, um verdächtige Aktivitäten zu erkennen und darauf zu reagieren.

### Beispielhafter Ablauf

1. **Registrierung**:
   - Der Benutzer registriert seine Authentifizierungs-App mit dem Desktop-Client.
   - Das mobile Gerät wird mit dem Desktop-Client verbunden.

2. **Anmeldung**:
   - Der Benutzer gibt seine Anmeldedaten auf dem Desktop-Client ein.
   - Der Desktop-Client fordert die Authentifizierung an und sendet eine Challenge an die Authentifizierungs-App auf dem mobilen Gerät.

3. **Challenge-Antwort**:
   - Der Benutzer öffnet die Authentifizierungs-App und gibt den generierten OTP ein oder genehmigt die Push-Benachrichtigung.
   - Die Antwort wird an den Server gesendet.

4. **Verifizierung und Zugriff**:
   - Der Server verifiziert die Antwort und gewährt oder verweigert den Zugriff auf den Desktop-Client.

### Zusammenfassung

Die Authentifizierung für einen Desktop-Client, bei der sich der Nutzer über sein mobiles Gerät authentifizieren kann, nutzt typischerweise eine Kombination aus Multi-Faktor-Authentifizierung, mobilen Authentifizierungs-Apps und modernen Sicherheitsprotokollen. Dieser Ansatz erhöht die Sicherheit, indem er die Stärken der mobilen Geräte für die Authentifizierung nutzt und sicherstellt, dass der Zugriff auf den Desktop-Client nur nach erfolgreicher Bestätigung durch das mobile Gerät gewährt wird.

## Authentifizierung mit eGK

Eine Authentifizierung mit einem Desktop-Client und einer Smartcard ist eine weit verbreitete Methode, um sicherzustellen, dass nur autorisierte Benutzer auf ein System zugreifen können. Hier ist eine detaillierte Beschreibung, wie dieser Authentifizierungsprozess typischerweise abläuft:

### 1. **Vorbereitung und Einrichtung**

1. **Smartcard und Kartenleser**:
   - Der Benutzer erhält eine Smartcard, die einen kryptografischen Schlüssel (privater Schlüssel) und andere Authentifizierungsinformationen enthält.
   - Ein Kartenleser wird am Desktop-Client angeschlossen, um die Smartcard zu lesen.

2. **Installation der Treiber und Middleware**:
   - Auf dem Desktop-Client werden Treiber und Middleware für den Kartenleser und die Smartcard installiert. Diese Software ermöglicht die Kommunikation zwischen der Smartcard und dem Betriebssystem.

3. **Smartcard-Integration**:
   - Die Smartcard wird im Desktop-Client registriert. Dies kann durch die Installation der benötigten Software und die Konfiguration des Systems zur Verwendung der Smartcard für die Authentifizierung geschehen.

### 2. **Anmeldeprozess**

1. **Einstecken der Smartcard**:
   - Der Benutzer steckt die Smartcard in den Kartenleser am Desktop-Client.

2. **Start des Anmeldevorgangs**:
   - Der Benutzer startet den Anmeldevorgang am Desktop-Client. Der Client fordert die Authentifizierung an und gibt an, dass eine Smartcard verwendet werden soll.

3. **PIN-Eingabe**:
   - Der Benutzer wird aufgefordert, die PIN der Smartcard einzugeben. Diese PIN ist ein persönlicher Identifikationscode, der die Smartcard schützt und sicherstellt, dass nur der autorisierte Benutzer auf die Smartcard zugreifen kann.
   - Die PIN wird sicher über die Smartcard an den Desktop-Client übermittelt und überprüft.

4. **Kryptografische Authentifizierung**:
   - Die Smartcard führt eine kryptografische Operation durch (z.B. digitale Signatur oder Verschlüsselung) unter Verwendung des privaten Schlüssels, der auf der Smartcard gespeichert ist.
   - Der Desktop-Client kommuniziert mit der Smartcard, um eine Authentifizierungsanfrage zu erstellen. Diese Anfrage könnte beispielsweise eine Herausforderung sein, die von der Smartcard signiert wird, um die Identität des Benutzers zu bestätigen.

5. **Validierung der Antwort**:
   - Die Smartcard signiert die Herausforderung oder führt eine andere kryptografische Operation durch und sendet die Antwort an den Desktop-Client.
   - Der Desktop-Client oder der Authentifizierungsserver überprüft die Antwort, um sicherzustellen, dass sie korrekt ist und von der richtigen Smartcard stammt.

6. **Zugriffsgewährung**:
   - Wenn die Authentifizierung erfolgreich ist, wird der Benutzerzugriff gewährt. Der Desktop-Client gibt dem Benutzer Zugriff auf das System oder die geschützten Ressourcen.

### 3. **Zusätzliche Sicherheitsmaßnahmen**

1. **Verwaltung von Zertifikaten**:
   - Smartcards enthalten oft digitale Zertifikate, die zur Identitätsbestätigung und zur Verschlüsselung verwendet werden. Diese Zertifikate werden in der Regel von einer Zertifizierungsstelle (CA) ausgestellt und müssen regelmäßig überprüft und erneuert werden.

2. **Smartcard-Verwaltung**:
   - Die Smartcard-Verwaltung umfasst das Erstellen, Verwalten und Sperren von Smartcards, PIN-Management und die Sicherstellung, dass die Smartcards sicher und aktuell sind.

3. **Integration in bestehende Authentifizierungssysteme**:
   - Smartcard-Authentifizierung kann in bestehende Authentifizierungssysteme integriert werden, wie z.B. Single Sign-On (SSO) oder Active Directory. Dies ermöglicht eine nahtlose Authentifizierung über verschiedene Systeme hinweg.

4. **Sicherheitsüberwachung**:
   - Sicherheitsprotokolle und Überwachungssysteme können verwendet werden, um sicherzustellen, dass nur autorisierte Benutzer Zugang zu kritischen Ressourcen erhalten und um unregelmäßige Anmeldeversuche zu erkennen.

### 4. **Beispielhafter Ablauf**

1. **Vorbereitung**:
   - Benutzer erhält eine Smartcard und installiert die erforderliche Middleware auf dem Desktop-Client.
   - Benutzer steckt die Smartcard in den Kartenleser.

2. **Anmeldung**:
   - Benutzer startet den Anmeldevorgang und gibt die PIN für die Smartcard ein.
   - Der Desktop-Client fordert die Smartcard auf, eine kryptografische Antwort auf eine Authentifizierungsherausforderung zu erstellen.

3. **Authentifizierung**:
   - Die Smartcard signiert die Herausforderung und sendet die Antwort an den Desktop-Client.
   - Der Desktop-Client überprüft die Signatur und gewährt den Zugriff, wenn die Authentifizierung erfolgreich ist.

4. **Zugriffsgewährung**:
   - Benutzer erhält Zugriff auf den Desktop-Client oder die geschützten Ressourcen.

### Zusammenfassung

Die Authentifizierung mit einem Desktop-Client und einer Smartcard bietet eine starke Sicherheitsmethode, indem sie physische und kryptografische Faktoren kombiniert. Der Prozess umfasst das Einstecken der Smartcard, die Eingabe einer PIN, die Durchführung kryptografischer Operationen durch die Smartcard und die Überprüfung der Authentifizierung durch den Desktop-Client oder den Authentifizierungsserver. Diese Methode verbessert die Sicherheit durch die Kombination von etwas, das der Benutzer hat (die Smartcard), und etwas, das der Benutzer weiß (die PIN).