# TPM und Trust-Client

##  Anforderungen

- Schlüssel dauerhaft speichern, der für Signatur von DPoP Schlüssel verwendet wird
- TPM Schlüssel darf nur vom Trust Client verwendet werden, aber von jedem Nutzer
- PCRs erstellen, der hash vom Trust-Client enthält, der nur von der Trust-Client-Anwendung ausgelesen werden kann
- Trust-Client überprüft seinen Code mit Hash aus PCR um die Integrität zu verifizieren
- Afos nicht nur für Windows formulieren; auch für Linux und MacOS.
- Geräteregistrierung mit SMC-B muss das Remote Attestation Verfahren mit TPM nutzen. D. h. erst Authentisierung mit SM-B über Client Assertion JWT. Ergebnis ist Access Token mit Scope Client-Registrierung. Dann Clientregistrierung mit Remote Attestation Verfahren. Danach kann der Cient ein Access Token für den  resource Server am /token Endpunkt abfragen.
- Ablauf für SM-B Authentifizierung muss für TPM Nutzung angepasst werden (TPM für Geräte-Registrierung, SM-B für Authentifizierung)

## Was wird an den AuthS übermittlet

- Dynamic Client Registration (DCR) mit TPM
- Option: (weitere Analyse notwendig) hash des Trust Clients aus TPM (geht unter Windows Enterprise mit WDAC). Policy Engine hat über PIP eine Liste der verwendeten Trust-Clients aller Hersteller inkl. der Hashes der Trust-Clients und kann prüfen, ob der hash aus dem TPM übereinstimmt
- Posture

## Sicherheitsbeurteilung

**Bedrohung**
Mit Admin Rechten kann ein Angreifer einen bad Trust-Client verwenden, ohne dass Zero Trust das merkt. -> muss geprüft werden.

### Posture Beispiel Schema
Beispiel-Schema für das `posture`-Attribut einer Client-Instanz in einem Zero Trust-Kontext. Dieses Attribut beschreibt die Sicherheitslage (Posture) der Client-Instanz und umfasst mehrere Aspekte wie Betriebssystemversion, Patch-Status, Antivirus-Status usw. Nach dem Schema folgen Erklärungen zu den einzelnen Komponenten.

Das **Posture**-Schema wurde um Informationen erweitert, die im Zusammenhang mit dem Trusted Platform Module (TPM) und dem Bootprozess stehen (BIOS, Boot-Loader, OS Kernel)

#### Erweiterte Beispiel-Schema für `posture`

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
Posture:
  type: object
  properties:
    os_version:
      type: string
      description: "The version of the operating system running on the client instance."
    patch_level:
      type: string
      description: "The current patch level of the client instance, indicating the latest security updates installed."
    antivirus_installed:
      type: boolean
      description: "Indicates whether an antivirus software is installed on the client instance."
    antivirus_status:
      type: string
      enum: ["up_to_date", "outdated", "not_installed"]
      description: "The status of the antivirus software, indicating whether it is up to date, outdated, or not installed."
    encryption_enabled:
      type: boolean
      description: "Indicates whether disk encryption is enabled on the client instance."
    firewall_enabled:
      type: boolean
      description: "Indicates whether the firewall is enabled on the client instance."
    last_checked:
      type: integer
      description: "The Unix timestamp indicating the last time the posture was checked."
    tpm_status:
      type: string
      enum: ["enabled", "disabled", "not_present"]
      description: "The status of the TPM (Trusted Platform Module) on the client instance."
    bios_version:
      type: string
      description: "The version of the BIOS firmware installed on the client instance."
    bios_integrity:
      type: boolean
      description: "Indicates whether the integrity of the BIOS firmware has been verified by the TPM."
    boot_loader_version:
      type: string
      description: "The version of the boot loader used during the system boot process."
    boot_loader_integrity:
      type: boolean
      description: "Indicates whether the integrity of the boot loader has been verified by the TPM."
    os_kernel_version:
      type: string
      description: "The version of the operating system kernel loaded during the boot process."
    os_kernel_integrity:
      type: boolean
      description: "Indicates whether the integrity of the operating system kernel has been verified by the TPM."
  required:
    - os_version
    - patch_level
    - antivirus_installed
    - antivirus_status
    - encryption_enabled
    - firewall_enabled
    - last_checked
    - tpm_status
    - bios_version
    - bios_integrity
    - boot_loader_version
    - boot_loader_integrity
    - os_kernel_version
    - os_kernel_integrity
```

#### Erläuterungen zu den neuen Attributen

1. **os_version**:
   - **Typ**: `string`
   - **Beschreibung**: Diese Eigenschaft gibt die Version des Betriebssystems an, das auf der Client-Instanz läuft. Dies ist wichtig, um sicherzustellen, dass das Betriebssystem auf dem neuesten Stand ist und keine bekannten Sicherheitslücken aufweist.

2. **patch_level**:
   - **Typ**: `string`
   - **Beschreibung**: Gibt den aktuellen Patch-Stand des Clients an. Der Patch-Level ist entscheidend, um zu verstehen, ob alle sicherheitsrelevanten Updates auf dem System installiert wurden.

3. **antivirus_installed**:
   - **Typ**: `boolean`
   - **Beschreibung**: Ein boolescher Wert, der anzeigt, ob auf der Client-Instanz eine Antivirus-Software installiert ist. Ein installiertes Antivirus-Programm ist ein wichtiger Aspekt der Sicherheitslage.

4. **antivirus_status**:
   - **Typ**: `string`
   - **Beschreibung**: Gibt den Status der Antivirus-Software an. Die möglichen Werte sind:
     - **up_to_date**: Die Antivirus-Software ist auf dem neuesten Stand und bietet maximalen Schutz.
     - **outdated**: Die Antivirus-Software ist veraltet und könnte daher weniger wirksam sein.
     - **not_installed**: Keine Antivirus-Software ist installiert.
   - **Hinweis**: Dieses Feld hilft dabei, die Wirksamkeit des Sicherheitsmechanismus zu bewerten.

5. **encryption_enabled**:
   - **Typ**: `boolean`
   - **Beschreibung**: Gibt an, ob die Festplattenverschlüsselung auf der Client-Instanz aktiviert ist. Festplattenverschlüsselung ist ein wichtiger Schutzmechanismus, um Datenverlust und unbefugten Zugriff zu verhindern.

6. **firewall_enabled**:
   - **Typ**: `boolean`
   - **Beschreibung**: Ein boolescher Wert, der angibt, ob die Firewall auf der Client-Instanz aktiviert ist. Eine aktive Firewall hilft dabei, unerwünschten Netzwerkverkehr zu blockieren und erhöht somit die Sicherheit.

7. **last_checked**:
   - **Typ**: `integer`
   - **Beschreibung**: Der Unix-Zeitstempel, der den Zeitpunkt angibt, zu dem die Sicherheitslage zuletzt überprüft wurde. Diese Information ist nützlich, um zu beurteilen, wie aktuell die Informationen zur Sicherheitslage sind.

8. **tpm_status**:
   - **Typ**: `string`
   - **Beschreibung**: Gibt den Status des Trusted Platform Modules (TPM) auf der Client-Instanz an. Die möglichen Werte sind:
     - **enabled**: Das TPM ist aktiviert und einsatzbereit.
     - **disabled**: Das TPM ist deaktiviert.
     - **not_present**: Kein TPM-Modul auf der Client-Instanz vorhanden.

9. **bios_version**:
   - **Typ**: `string`
   - **Beschreibung**: Gibt die Version der BIOS-Firmware an, die auf der Client-Instanz installiert ist. Dies ist wichtig, da die BIOS-Version oft sicherheitsrelevante Updates enthält.

10. **bios_integrity**:
   - **Typ**: `boolean`
   - **Beschreibung**: Ein boolescher Wert, der angibt, ob die Integrität der BIOS-Firmware durch das TPM erfolgreich verifiziert wurde. Eine positive Verifizierung bedeutet, dass die BIOS-Firmware seit dem letzten Boot-Vorgang nicht manipuliert wurde.

11. **boot_loader_version**:
   - **Typ**: `string`
   - **Beschreibung**: Die Version des Bootloaders, der während des Systemstarts verwendet wurde. Der Bootloader ist eine kritische Komponente im Bootprozess, da er den Kernel des Betriebssystems lädt.

12. **boot_loader_integrity**:
   - **Typ**: `boolean`
   - **Beschreibung**: Ein boolescher Wert, der anzeigt, ob die Integrität des Bootloaders durch das TPM verifiziert wurde. Eine erfolgreiche Verifizierung zeigt, dass der Bootloader nicht manipuliert wurde.

13. **os_kernel_version**:
   - **Typ**: `string`
   - **Beschreibung**: Die Version des Betriebssystem-Kernels, der während des Bootprozesses geladen wurde. Diese Information ist wichtig für die Sicherheitslage, da Kernel-Updates oft kritische Sicherheitslücken schließen.

14. **os_kernel_integrity**:
   - **Typ**: `boolean`
   - **Beschreibung**: Ein boolescher Wert, der anzeigt, ob die Integrität des Betriebssystem-Kernels durch das TPM verifiziert wurde. Dies stellt sicher, dass der Kernel nicht manipuliert wurde, bevor er in den Speicher geladen wurde.

### Nutzungsszenario
Dieses `posture`-Schema ist ein integraler Bestandteil einer Zero Trust Architektur, in der jede Client-Instanz regelmäßig überprüft wird, um sicherzustellen, dass sie den Sicherheitsanforderungen entspricht. Die Informationen aus dem `posture`-Objekt können verwendet werden, um Entscheidungen über den Zugang zu sensiblen Ressourcen zu treffen oder um bestimmte Sicherheitsmaßnahmen durchzusetzen.
Die TPM-bezogenen Informationen ermöglichen eine detaillierte Überprüfung des gesamten Bootprozesses einer Client-Instanz. Diese Informationen sind besonders wichtig in sicherheitskritischen Umgebungen, wo Manipulationen am BIOS, Bootloader oder Kernel schwerwiegende Sicherheitsrisiken darstellen könnten. Durch die Einbeziehung des TPMs können diese Komponenten überwacht und deren Integrität sichergestellt werden.

## TPM Attestation Key

Sehr gute Frage – und die Antwort ist: **es kommt darauf an**, aber meistens **muss ein eigener Schlüssel erzeugt werden**, speziell für deinen Client oder deine Anwendung.

Hier die Details:

---

### 🔐 **AIK (Attestation Key) im TPM – Grundlagen**

1. **AIK = Attestation Key**
   - Das ist ein spezieller TPM-Schlüssel, der verwendet wird, um Attestationsdaten zu signieren (z. B. PCR-Werte oder Zertifikate anderer TPM-Schlüssel).
   - Früher war „AIK“ eher eine Bezeichnung in TPM 1.2. In TPM 2.0 nennt man das „Attestation Key“ oder „Restricted Signing Key“.

2. **Nicht automatisch vorhanden**
   - Der TPM kommt **nicht mit einem vorinstallierten AIK**.
   - Anwendungen (wie ein TPM-fähiger Client oder Identity Agent) **müssen selbst einen AIK erzeugen**, typischerweise unter Verwendung des Endorsement Key (EK) als Vertrauensanker.

3. **Wie der AIK erzeugt wird (TPM 2.0):**
   - Du erzeugst einen „restricted signing key“ mit:
     - `signing = true`
     - `restricted = true`
     - `fixedTPM = true`
     - `fixedParent = true`
   - Dieser Schlüssel ist **nicht exportierbar** (private part bleibt im TPM).
   - Das TPM kann dir eine **zertifizierbare Beschreibung** des Schlüssels liefern (`TPM2_Certify`), die du mit dem EK-Zertifikat und einer Signatur verifizieren kannst.

---

Verwende `tpm2-tools` oder `tpm2-pytss`) um einen Attestation Key zu erzeugen.

### 🧪 **Ziel**  
- Erzeuge einen AIK im TPM  
- Zertifiziere einen zweiten TPM-Schlüssel (z. B. ein "normaler" Client-Schlüssel)  
- Signiere die nonce vom AS mit dem AIK

### ⚙️ Voraussetzungen

- TPM 2.0 aktiv  
- `tpm2-tools` installiert (`sudo apt install tpm2-tools`)  
- Zugriff auf `/dev/tpm0` oder Simulator

---

### 🔧 **Schritte mit `tpm2-tools`**

#### 1. Erzeuge den AIK-Schlüssel (signing, restricted)

```bash
sudo tpm2_createprimary -C e -c aik.ctx -g sha256 -G rsa
sudo tpm2_create -C aik.ctx -u aik.pub -r aik.priv -c aik_key.ctx \
  -a "fixedtpm|fixedparent|sensitivedataorigin|userwithauth|restricted|sign"
```

💡 Jetzt hast du:
- `aik_key.ctx` → AIK Schlüsselkontext
- `aik.pub`, `aik.priv` → Public & Private Teile (nur für TPM intern)

#### 2. Lade den AIK ins TPM (optional, falls neu geladen werden muss)

```bash
sudo tpm2_load -C aik.ctx -u aik.pub -r aik.priv -c aik_key.ctx
```

---

#### 3. Erzeuge einen **normalen TPM-Schlüssel**, der zertifiziert werden soll (z. B. Client-Schlüssel)

```bash
tpm2_create -C aik.ctx -u client.pub -r client.priv -c client_key.ctx \
  -a "fixedtpm|fixedparent|sensitivedataorigin|userwithauth|sign"
```

---

#### 4. Zertifiziere den **Client-Schlüssel** mit dem AIK

```bash
tpm2_certify -C aik_key.ctx -c client_key.ctx -g sha256 \
  -o certify.sig -f plain -q qualify.data -a
```

Ergebnis:
- `certify.sig` → Signatur über die Zertifizierungsdaten
- `qualify.data` → Inhalt der Zertifizierungsnachricht (z. B. Digest über Public Key)

---

#### 5. (Optional) Verifiziere das Zertifikat

```bash
openssl dgst -sha256 -verify <(tpm2_readpublic -c aik_key.ctx -f pem | awk '/-BEGIN/{f=1}f') \
  -signature certify.sig qualify.data
```

Wenn du ein `Verified OK` siehst → alles korrekt!

---

### 📁 Zusammenfassung der Dateien

| Datei           | Inhalt                        |
|----------------|-------------------------------|
| `aik_key.ctx`   | Kontext des AIK im TPM        |
| `client_key.ctx`| Kontext des zu zertifizierenden Schlüssels |
| `certify.sig`   | Signatur des AIK              |
| `qualify.data`  | Zertifizierungsnachricht      |

---
#### 
Ein **TCG Event Log** (auch „TPM Event Log“ oder „TCG PCR Event Log“) ist eine strukturierte Datei, die beschreibt, **welche sicherheitsrelevanten Ereignisse während des Systemstarts stattgefunden haben** – speziell im Zusammenhang mit dem **TPM (Trusted Platform Module)**.

Dabei steht **TCG** für die **Trusted Computing Group**, die die Spezifikationen für TPM und das Event Logging definiert.

---

### 📦 Was ist im TCG Event Log enthalten?

Der TCG Event Log enthält eine **Sequenz von Events**, die jeweils dokumentieren:

- Was für ein Ereignis aufgetreten ist (z. B. Firmware geladen, Secure Boot Policy, EFI Treiber, Bootloader, OS Kernel, etc.)
- Welcher Hashwert (Digest) berechnet wurde
- In welchen PCRs (Platform Configuration Registers) dieser Hash extendet wurde
- Optionale Zusatzinfos (Name, Daten, Herstellerinfos)

---

### 🔄 Zusammenhang mit TPM & PCRs

Der TPM speichert in **PCRs** nur die **Hash-Ketten**, nicht die Inhalte der geladenen Komponenten.

👉 Der **Event Log** liefert die **semantischen Informationen**, die zu den Hashes gehören, also:
- Was genau wurde gehasht?
- Welche Software oder Firmware war beteiligt?
- Wie wurde das Hash berechnet?

➡️ Damit kannst du ein **„Measured Boot“** rekonstruieren, also:
- Prüfen, was geladen wurde
- Sicherstellen, dass keine unerwartete Software beteiligt war

---

### 🧾 Beispiel für ein Event (vereinfacht)

```json
{
  "PCRIndex": 0,
  "EventType": "EV_POST_CODE",
  "Digest": "e3b0c442...b855",
  "Event": "BIOS Startup Module"
}
```

---

### 📍 Wo findet man den Event Log?

- Unter **Linux**:
  - `cat /sys/kernel/security/tpm0/binary_bios_measurements`
  - Tools wie `tpm2_eventlog` aus `tpm2-tools` können das lesbar machen:
    ```bash
    tpm2_eventlog /sys/kernel/security/tpm0/binary_bios_measurements
    ```

- Unter **Windows**:
  - Der Event Log ist im RAM und über APIs zugreifbar (z. B. über Windows Defender System Guard, oder `TBS`-APIs)
  - Tools wie `tpmtool getdeviceinformation` oder Drittsoftware können helfen

---

### 🛡️ Wofür wird das verwendet?

- **Remote Attestation**: Ein Remote-Server kann sich die PCR-Werte und den Event Log geben lassen und verifizieren, ob das System vertrauenswürdig gebootet wurde.
- **Bootintegritätsprüfung**: Überprüfen, ob alle Bestandteile des Boot-Prozesses im erwarteten Zustand waren.
- **Policy Enforcement**: Zugriff nur erlauben, wenn bestimmte Events in bestimmten PCRs sind (z. B. nur mit signiertem Kernel).

---

### ⚠️ Wichtig

- Der Event Log ist **nicht kryptographisch gesichert**, sondern nur die **PCRs im TPM**.
- Wenn man den Event Log **nicht überprüft**, kann man nicht wissen, was gehasht wurde – nur, **dass etwas gehasht wurde**.

---

Wenn du willst, zeige ich dir gerne:
- wie man mit `tpm2_eventlog` den Log parst,
- oder wie man ein eigenes Event Log im Attestation-Flow mitliefert.  
Lust drauf?

Sehr gute Frage – und sie trifft genau den Kern aktueller Diskussionen rund um **Application Layer Attestation**.

---

### ✅ **Kurzantwort:**

- **App ID, App Version und App Signature Hash** _**sind nicht standardmäßig**_ im **TCG Event Log** enthalten.
- **Aber: Sie können dort eingetragen werden**, **wenn** das System sie im Rahmen des Boot- oder Launch-Prozesses in den TPM (PCRs) „extendet“ und dabei im Event Log dokumentiert.
- **Sicher eintragen** lässt sich das nur, **wenn die Komponente, die das macht, vertrauenswürdig ist** (z. B. der OS Loader oder ein gemessener Attestation Agent im Kernelspace oder Secure Boot Chain).

---

### 🧠 **Hintergrund:**

#### 📦 Der TCG Event Log enthält:
- **Firmware-/Bootloader-Events** (UEFI, Bootloader, Kernel)
- Secure Boot Policy & Schlüssel
- Kernel Command Line
- Module (z. B. initrd)
- Optional: eigene Events von OS oder TPM-Software

#### ❌ Was fehlt:
- **Applikationen im Userspace** (z. B. dein OAuth Client oder deine App)  
  werden **nicht automatisch gemessen oder geloggt**.

---

### 🛠️ **Wie könnte man App-Daten sicher eintragen?**

#### ✅ **Möglichkeit 1: App Measurement durch den OS Loader oder IMA**

- **Linux:**
  - Nutze das **Integrity Measurement Architecture (IMA)** Framework.
  - Das kann beim Starten von User-Apps automatisch:
    - Hashes von Executables berechnen
    - Signature Hashes prüfen
    - Event Log-Einträge erzeugen
    - PCRs extenden
  - ➕ Vorteil: Automatisch, standardisiert, mit TPM verknüpfbar

- **Windows:**
  - Nutzt z. B. Windows Defender Application Control (WDAC) oder VBS
  - App-Zertifikate, Signaturen, File Hashes können gemessen werden
  - **Event Log-Einträge** können über Windows Measurement Events erzeugt werden

---

#### ✅ **Möglichkeit 2: Eigene TPM Extend + Event Log API**

Du kannst als Entwickler:
- **Eigene Events erzeugen**
- z. B. beim App-Start:  
  - `App ID = "com.example.client"`  
  - `App Version = "1.2.3"`  
  - `Signature Hash = SHA256(...)`
- Diese Daten:
  - in einen Digest umwandeln
  - in eine PCR schreiben (`TPM2_PCR_Extend`)
  - und gleichzeitig als Event im Event Log notieren

➡️ Aber: Du brauchst dazu ein **vertrauenswürdiges Modul**, das das macht (nicht beliebiger Userspace-Code).

---

### 🛡️ **Sicherheitsanforderung**

Damit das **sicher** ist, muss gelten:

| Kriterium | Erklärung |
|----------|-----------|
| ✅ **Authentizität** | Die Komponente, die die App misst, muss selbst gemessen sein (UEFI, Kernel, IMA, VBS) |
| ✅ **Unverfälschbarkeit** | Die gemessenen Daten landen im TPM (PCR) → vor Manipulation geschützt |
| ✅ **Verifizierbarkeit** | Der Event Log + PCR kann vom Remote Server (z. B. OAuth Server) validiert werden |

---

### 📌 Beispiel: Linux mit IMA (inkl. App Hash)

```bash
# Beispielauszug aus einem IMA Event Log
PCRIndex: 10
EventType: IMA
Digest: 74d760...
TemplateName: ima-sig
Event: /usr/bin/myapp | hash=sha256:abc123... | signer=X.509-CN=ACME Inc
```

---

### Fazit:

| Frage | Antwort |
|-------|---------|
| Können App-Daten im TCG Event Log enthalten sein? | ✅ Ja, **aber nur**, wenn sie vom OS oder einer vertrauenswürdigen Komponente gemessen werden |
| Wie kann man sie sicher eintragen? | Über IMA (Linux), WDAC (Windows), oder eigene trusted Komponenten, die den TPM korrekt ansprechen |

---


### 🧩 **Was ist WDAC?**
WDAC ist ein Mechanismus zur Durchsetzung von Code-Integritätsrichtlinien in Windows, der gleichzeitig mit **Virtualization-Based Security (VBS)** und dem **Windows Boot-Measurement-Stack** zusammenarbeitet, um:
- Nur zugelassene (signierte) Binärdateien auszuführen,
- Diese beim Start zu messen (→ TPM PCR Extend),
- Den Event Log mit Infos über die App, Signatur, Hash etc. zu füllen.

---

### ✅ **Technische Voraussetzungen für WDAC + TPM Measurements**

#### 🖥️ 1. **Windows 10/11 Enterprise oder Education**
- **WDAC ist nur vollständig verfügbar** in **Enterprise** und **Education** Versionen.
- **Pro/Home** bieten keine vollständige Unterstützung für Code Integrity Enforcement und App Measurement.

#### 🔐 2. **Secure Boot aktiviert**
- Secure Boot muss aktiv sein, damit die Boot- und OS-Komponenten vollständig gemessen werden.
- WDAC hängt an der Secure-Boot-Kette.

#### 🧠 3. **VBS (Virtualization-Based Security) aktiviert**
- Aktiviert über Gruppenrichtlinie oder Device Guard.
- Benötigt:
  - UEFI Firmware
  - Second Level Address Translation (SLAT)
  - Trusted Boot

#### 🧱 4. **Code Integrity Policies (CI-Policy) definiert**
- Du musst eine CI-Policy schreiben, z. B.:
  - nur Apps mit bestimmten Publisher-Zertifikaten erlauben
  - oder nur bestimmte Hashes
- Die Policy aktiviert auch das **Measurement Logging**

Beispiel einer Policy-Zeile:

```xml
<FileRules>
  <FileRule Id="MyAppRule" FriendlyName="My App" Action="Allow">
    <FileName>myapp.exe</FileName>
    <FileVersionRange Min="1.2.3.0" Max="1.2.3.0" />
    <SignerId>MyCodeSigningCert</SignerId>
  </FileRule>
</FileRules>
```

#### 📄 5. **CI Policy im Kernel-Modus aktiviert (Audit oder Enforce)**
- Nur dann findet auch TPM Measurement statt.
- Aktivierung per:
  ```powershell
  Set-RuleOption -FilePath MyPolicy.xml -Option 0 # Enables Audit Mode
  ConvertFrom-CIPolicy -XmlFilePath MyPolicy.xml -BinaryFilePath MyPolicy.bin
  ```
- Laden per:
  ```powershell
  Add-CodeIntegrityPolicy -PolicyPath MyPolicy.bin -PolicyFormat P7B
  ```

#### 🧪 6. **App Signierung mit einem vertrauenswürdigen Zertifikat**
- Dein App-Binary muss signiert sein.
- Die Signatur muss von der Policy erlaubt sein.
- Nur dann erscheint dein App-Hash, die Signatur und ggf. Metadaten im Event Log.

---

### 📑 **Was landet im Event Log?**

Wenn deine App unter WDAC ausgeführt wird (mit aktivem CI + Measurement Logging), kann der Event Log folgendes enthalten:

| Feld              | Beschreibung                         |
|-------------------|--------------------------------------|
| App Pfad          | Vollständiger Pfad zu deiner `.exe`  |
| SHA-256 Hash      | Hash der Datei                       |
| Signer Info       | Subject CN/OU/Issuer der Signatur    |
| App Version Info  | Aus PE-Headers (falls vorhanden)     |

Diese Daten werden dann auch **in PCR 11 (oder 12+) extendet** und tauchen im **Measured Boot Log** auf.

---

### 🔎 Nachsehen: Was wurde gemessen?

1. **Event Log ansehen:**
   ```powershell
   Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational"
   ```

2. **TPM Event Log parsen:**
   Tools wie [`tpmtool`](https://learn.microsoft.com/en-us/windows/security/information-protection/tpm/tpmtool) oder [`tpm2_eventlog`] auf Linux

---

### ✅ Zusammengefasst: Voraussetzungen für WDAC + TPM Measurement deiner App

| Voraussetzung | Erfüllt durch |
|---------------|---------------|
| Windows 10/11 Enterprise/Education | OS-Lizenz |
| Secure Boot aktiviert | UEFI + BIOS Settings |
| VBS aktiviert | OS + Hardware-Support |
| CI-Policy mit Signaturen/Hashes | XML-Richtlinie |
| App signiert mit akzeptiertem Cert | Entwickler |
| Policy aktiv im Enforce/Audit Mode | Admin |

---
Sehr gute und sehr tiefgehende Frage!  
Die kurze Antwort ist:  
👉 **Man benötigt nicht grundsätzlich Adminrechte, um mit einem AIK zu signieren** – **aber oft schon**, **je nach TPM-Konfiguration**, weil die **AIK einem geschützten Hierarchiebereich** im TPM zugeordnet ist.

---

### 🧠 Hintergrund: Warum braucht man manchmal Adminrechte, um mit dem AIK zu signieren?

#### 🔐 1. **AIK liegt in einer privilegierten TPM-Hierarchie**
Ein AIK wird typischerweise unter der **Endorsement Hierarchy (EH)** oder **Owner Hierarchy (OH)** erstellt. Diese sind **standardmäßig geschützt**:

- Zugriff erfordert ein TPM-Authorization-Policy
- Diese Policy ist oft so eingestellt, dass nur Prozesse mit **Systemrechten oder Adminrechten** auf den Schlüssel zugreifen dürfen

**→ Das betrifft alle Operationen mit dem AIK**, nicht nur das Erzeugen, sondern auch:
- Laden (`tpm2_load`)
- Verwenden zum Signieren (`tpm2_sign`)
- Zertifizieren von PCRs (`tpm2_quote`)

---

#### 🛡️ 2. **AIKs sind als “Restricted Keys” deklariert**
Wenn du den AIK mit dem Attribut `restricted` erzeugst (wie es spezifiziert ist):

```bash
tpm2_createprimary -C e -g sha256 -G rsa -a "restricted|sign|fixedtpm|fixedparent|sensitivedataorigin|userwithauth"
```

…dann darf dieser Schlüssel **nur für ganz bestimmte Signaturtypen verwendet werden**, z. B.:
- `TPM2_Quote` (Quote über PCRs)
- `TPM2_Certify` (Signieren eines Objekts mit AIK)

**Nicht erlaubt:** beliebige Nutzdaten signieren (`tpm2_sign`) → auch das kann wie eine Art Schutzmaßnahme wirken.

---

#### 🔒 3. **Authorisierung via TPM-Policy**
Die AIK hat ein **AuthValue (Passwort)** oder eine **PolicyDigest**, die beim Zugriff erfüllt sein muss.  
Je nach Konfiguration brauchst du dann:
- Zugriff auf gespeicherte Schlüssel-Handles (`tpm2_evictcontrol`)
- Oder TPM-Sessions mit passender Policy
- Oder du musst den Schlüssel frisch laden mit Auth-Werten, die nur **Admins** kennen

---

### 🪟 Unter Windows: Noch restriktiver

Windows verwaltet AIKs **unter Windows Hello for Business / Device Health Attestation / Credential Guard** – d. h.:

- Der AIK wird oft vom System (LSA, Credential Guard) verwendet
- Zugriff auf AIK → nur über das **Device Health Attestation Framework**
- **Nicht direkt zugänglich aus Usermode**, auch nicht aus Admin-Konten

---

### ⚙️ Ausnahmen: Wann _braucht_ man **keine** Adminrechte?

Du **kannst auch einen eigenen AIK-artigen Schlüssel** erzeugen, z. B.:

```bash
tpm2_createprimary -C o -c myaik.ctx -g sha256 -G ecc
```

- **Nicht unter der Endorsement Hierarchy** (`-C o` statt `-C e`)
- Ohne Policy
- Ohne `restricted`

Damit kannst du **als normaler User** in vielen TPMs signieren. Aber:

- Es ist kein „klassischer AIK“, wie ihn z. B. ein Attestation Server akzeptieren würde
- Er ist nicht zertifiziert und nicht durch EK gebunden
- Weniger vertrauenswürdig für Remote Attestation

---

### ✅ Zusammenfassung

| Frage | Antwort |
|-------|---------|
| **Braucht man Adminrechte, um mit einem AIK zu signieren?** | **In der Regel ja**, weil AIKs unter einer geschützten Hierarchie liegen und TPM Policies greifen |
| **Kann man das umgehen?** | Ja – durch eigenen nicht-privilegierten Schlüssel, aber dann ist es **kein "echter" AIK** |
| **Gibt es Alternativen?** | TPM Quote über PCRs mit AIK ist oft der sichere und akzeptierte Weg für Remote Attestation – wird vom AIK signiert, nicht willkürliche Daten |

### Beispiel in Python

Super – für echte **Remote Attestation mit TPM 2.0** in Python brauchst du im Wesentlichen drei Dinge:

1. **Erstellung eines AIK (Attestation Identity Key)** im TPM  
2. **Erstellung einer Quote über bestimmte PCRs**, signiert mit dem AIK  
3. **Ausgabe der Quote, des zugehörigen Nonces und des Event Logs** zur Verifikation durch einen Remote Attestation Server

---

### 📦 Voraussetzungen

- TPM2-Hardware oder Simulator
- `tpm2-tools` (für Setup)
- Python-Paket: [`tpm2-pytss`](https://github.com/tpm2-software/tpm2-pytss)

Installiere:
```bash
pip install tpm2-pytss
```

---

### 🐍 Beispiel-Skript in Python: **Quote mit AIK über PCRs 0,1,2**

```python
from tpm2_pytss import *
from tpm2_pytss.util.simulator import Simulator
from hashlib import sha256
import os
import binascii

# Initialisierung
tcti = TCTILdr("device")
esys = ESAPI(tcti)

# PCRs, die gemessen werden sollen
pcr_selection = TPML_PCR_SELECTION()
pcr_selection.count = 1
pcr_selection.pcr_selections[0].hash = TPM2_ALG.SHA256
pcr_selection.pcr_selections[0].sizeofSelect = 3
pcr_selection.pcr_selections[0].pcrSelect[0] = 0b00000111  # PCR 0,1,2

# 1. Erstelle den AIK als Restricted Signing Key
in_public = TPM2B_PUBLIC(
    publicArea=TPMT_PUBLIC(
        type=TPM2_ALG.ECC,
        nameAlg=TPM2_ALG.SHA256,
        objectAttributes=(TPMA_OBJECT.RESTRICTED | TPMA_OBJECT.USERWITHAUTH |
                          TPMA_OBJECT.SIGN_ENCRYPT | TPMA_OBJECT.FIXEDTPM |
                          TPMA_OBJECT.FIXEDPARENT | TPMA_OBJECT.SENSITIVEDATAORIGIN),
        parameters=TPMU_PUBLIC_PARMS(
            eccDetail=TPMS_ECC_PARMS(
                symmetric=TPMT_SYM_DEF_OBJECT(algorithm=TPM2_ALG.NULL),
                scheme=TPMT_ECC_SCHEME(scheme=TPM2_ALG.ECDSA, details=TPMU_ASYM_SCHEME(ecdsa=TPMS_SCHEME_HASH(hashAlg=TPM2_ALG.SHA256))),
                curveID=TPM2_ECC.NIST_P256,
                kdf=TPMT_KDF_SCHEME(scheme=TPM2_ALG.NULL)
            )
        ),
        unique=TPMU_PUBLIC_ID(ecc=TPMS_ECC_POINT(x=TPM2B_ECC_PARAMETER(), y=TPM2B_ECC_PARAMETER()))
    )
)

primary_handle, out_public, _, _, _ = esys.CreatePrimary(
    ESYS_TR.ENDORSEMENT,
    inSensitive=TPM2B_SENSITIVE_CREATE(),
    inPublic=in_public,
)

# 2. Quote erzeugen mit Nonce
nonce = os.urandom(20)
quoted, signature = esys.Quote(
    primary_handle,
    qualifyingData=TPM2B_DATA(buffer=nonce),
    inScheme=TPMT_SIG_SCHEME(scheme=TPM2_ALG.NULL),
    PCRselect=pcr_selection
)

# 3. Drucke die Quote und Signature
print("Nonce:", binascii.hexlify(nonce).decode())
print("Quote:", binascii.hexlify(bytes(quoted.quote)).decode())
print("Signature:", binascii.hexlify(bytes(signature.signature.ecdsa.signatureR.buffer)).decode())

# 4. Eventlog auslesen (nur als Platzhalter)
print("Tipp: Eventlog separat mit `tpm2_eventlog /sys/kernel/security/tpm0/binary_bios_measurements` extrahieren.")

# Clean up
esys.FlushContext(primary_handle)
```

---

### 🔍 Was tut das Skript?

- Erstellt einen AIK (ECC NIST P-256, restricted, sign)
- Erstellt eine Quote über PCR 0,1,2 mit einem zufälligen Nonce
- Gibt Quote + Signatur aus
- Hinweis auf das Eventlog (separat auszulesen)

---

### 🧪 Verifikation der Quote (beim Attestation Server)

Der Remote Attestation Server braucht:
- Quote
- Public Key des AIK (aus `out_public`)
- Nonce (zum Schutz gegen Replay)
- PCR-Daten
- Eventlog zum Vergleich gegen bekannte „gute Zustände“

---

Wenn du magst, zeige ich dir gern auch:
- Wie du das Quote-Blob und die Signature base64-codiert für ein API übermittelst
- Oder wie man das Ganze in einem echten Attestation Workflow verwendet

Willst du auch ein **Verifikations-Skript** in Python auf Serverseite?

### WHA

Windows Health Attestation (WHA) ist ein Sicherheitsdienst von Microsoft, der Unternehmen und Entwicklern ermöglicht, den Sicherheitsstatus eines Windows-Geräts zu überprüfen. WHA nutzt das Trusted Platform Module (TPM) und andere Sicherheitsmechanismen, um vertrauenswürdige Informationen über den Zustand des Geräts zu liefern. Der Hauptzweck besteht darin, sicherzustellen, dass das Gerät vor dem Zugriff auf sensible Ressourcen oder Dienste in einem sicheren Zustand ist.

#### **Wie funktioniert WHA?**
WHA sammelt und überprüft verschiedene Sicherheitsmerkmale eines Windows-Geräts, darunter:
- **TPM-Status**: Ob das TPM aktiviert und funktionsfähig ist.
- **Secure Boot**: Ob das Gerät mit aktiviertem Secure Boot gestartet wurde, um sicherzustellen, dass nur vertrauenswürdige Software geladen wurde.
- **Codeintegrität**: Ob die Integrität des Betriebssystems gewährleistet ist.
- **BitLocker-Verschlüsselung**: Ob die Festplattenverschlüsselung aktiv ist.

Diese Informationen werden in einer sogenannten **Health Attestation Token (HAT)** zusammengefasst, die kryptografisch signiert ist und von einem Server oder einer Anwendung überprüft werden kann.

#### **Kann WHA für TPM Attestation bei Dynamic Client Registration verwendet werden?**
Ja, theoretisch kann WHA verwendet werden, um eine TPM-basierte Attestation während der Dynamic Client Registration (DCR) zu unterstützen. Allerdings gibt es einige wichtige Punkte zu beachten:

1. **TPM Attestation und WHA**:
   - WHA nutzt das TPM, um den Sicherheitszustand des Geräts zu bewerten. Das TPM kann kryptografische Schlüssel bereitstellen, die zur Identifikation und Verifizierung des Geräts verwendet werden können.
   - Während der Dynamic Client Registration (z. B. in OAuth 2.0 oder OpenID Connect), könnte eine TPM Attestation verwendet werden, um die Vertrauenswürdigkeit des Geräts zu bestätigen.

2. **Herausforderungen bei der Integration**:
   - WHA ist ein Microsoft-Dienst und erfordert, dass der Authorization Server (AS) in der Lage ist, die von WHA ausgestellten Health Attestation Tokens (HATs) zu verifizieren. Diese Token sind kryptografisch signiert und können nur überprüft werden, wenn der AS die entsprechenden Signaturzertifikate hat.
   - Die Unterstützung für WHA oder TPM Attestation muss explizit vom Authorization Server implementiert werden. Viele Standard-Authorization-Server unterstützen dies nicht von Haus aus.

3. **Alternativen oder Ergänzungen**:
   - Für eine direkte TPM Attestation könnte Ihr Authorization Server stattdessen den direkten Zugriff auf TPM-Funktionen nutzen, um eine Zertifikatskette oder eine kryptografische Signatur bereitzustellen, die den Zustand des Geräts authentifiziert.
   - WHA ist eher eine abstrakte Lösung, die den Sicherheitszustand eines Geräts beschreibt, während TPM Attestation oft spezifischere, TPM-zentrierte Informationen liefert.

#### **Kann ich WHA auf meinem Windows-PC verwenden?**
Das hängt davon ab, ob Ihr Gerät und Ihre Umgebung WHA unterstützen:
- **Voraussetzungen**:
  - Ihr Windows-PC muss über ein TPM (Trusted Platform Module) verfügen.
  - WHA ist in Windows 10 und Windows 11 integriert, aber es erfordert eine unterstützte Edition (z. B. Enterprise oder Pro).
  - Der Dienst erfordert eine Verbindung zu Microsoft-Diensten oder einem WHA-Server, der die Tokens ausstellt.

- **Einrichtung**:
  - WHA wird oft in Unternehmensumgebungen verwendet und ist normalerweise über MDM-Lösungen (Mobile Device Management) wie Microsoft Intune konfiguriert.
  - In einer individuellen Umgebung ist die Nutzung von WHA schwieriger, da es keine direkte Benutzeroberfläche gibt, um den Dienst zu aktivieren oder zu konfigurieren.

#### **Zusammenfassung**
Ja, WHA kann dazu beitragen, den Sicherheitszustand eines Windows-PCs zu attestieren, und TPM-basierte Attestation könnte während der Dynamic Client Registration verwendet werden. Allerdings:
- WHA ist primär für Unternehmensumgebungen gedacht.
- Der Authorization Server muss WHA-Token oder TPM Attestation explizit unterstützen.
- Für individuelle Geräte könnte es einfacher sein, direkt TPM-basierte Attestation zu implementieren, anstatt auf WHA zu setzen.

Falls Sie WHA in einer Entwicklungsumgebung nutzen möchten, könnte eine Integration mit einer MDM-Lösung oder die direkte Nutzung der TPM-APIs von Windows eine praktikablere Option sein.