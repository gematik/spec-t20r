# TPM und Trust-Client Anforderungen

- Schlüssel dauerhaft speichern, der für Signatur von DPoP Schlüssel verwendet wird
- TPM Schlüssel darf nur vom Trust Client verwendet werden, aber von jedem Nutzer
- PCRs erstellen, der hash vom Trust-Client enthält, der nur von der Trust-Client-Anwendung ausgelesen werden kann
- Trust-Client überprüft seinen Code mit Hash aus PCR um die Integrität zu verifizieren
- Afos nicht nur für Windows formulieren; auch für Linux und MacOS.
- Geräteregistrierung mit SMC-B muss das Remote Attestation Verfahren mit TPM nutzen. D. h. erst Authentisierung mit SM-B über Client Assertion JWT. Ergebnis ist Access Token mit Scope Client-Registrierung. Dann Clientregistrierung mit Remote Attestation Verfahren. Danach kann der Cient ein Access Token für den  resource Server am /token Endpunkt abfragen.
- Ablauf für SM-B Authentifizierung muss für TPM Nutzung angepasst werden (TPM für Geräte-Registrierung, SM-B für Authentifizierung)

## Was wird an den AuthS übermittlet

- Option: (weitere Analyse notwendig) hash des Trust Clients aus TPM. Policy Engine hat über PIP eine Liste der verwendeten Trust-Clients aller Hersteller inkl. der Hashes der Trust-Clients und kann prüfen, ob der hash aus dem TPM übereinstimmt
- Signatur des DPoP Schlüssels mit TPM Schlüssel
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
