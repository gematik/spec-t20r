# Pod-Sicherheit in Kubernetes

## Einführung

Das Sichern eines Pods in Kubernetes ist eine umfassende Aufgabe, die über reine Pod-Konfigurationen hinausgeht und die gesamte Kubernetes-Infrastruktur sowie betriebliche Prozesse mit einschließt. Es geht darum, eine "Defense-in-Depth"-Strategie zu implementieren.
Das Sichern eines Pods ist keine einmalige Aufgabe, sondern ein kontinuierlicher Prozess, der Überwachung, Wartung und Anpassung erfordert, um mit neuen Bedrohungen und Technologien Schritt zu halten.

## Inhaltsverzeichnis

- [Pod-Sicherheit in Kubernetes](#pod-sicherheit-in-kubernetes)
  - [Einführung](#einführung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Sichere Container-Images (Vor der Ausführung)](#sichere-container-images-vor-der-ausführung)
  - [Sichere Pod-Konfiguration und Laufzeit](#sichere-pod-konfiguration-und-laufzeit)
  - [Netzwerksicherheit](#netzwerksicherheit)
  - [Datenschutz und Geheimnisverwaltung](#datenschutz-und-geheimnisverwaltung)
  - [Cluster- und Infrastruktur-Sicherheit (Wirkt sich auf Pods aus)](#cluster--und-infrastruktur-sicherheit-wirkt-sich-auf-pods-aus)
  - [Betriebliche und Prozessuale Maßnahmen](#betriebliche-und-prozessuale-maßnahmen)
  - [Weiterführende Referenzen](#weiterführende-referenzen)

---

## Sichere Container-Images (Vor der Ausführung)

1. **Verwendung vertrauenswürdiger Basis-Images:**
   - Nutzen Sie offizielle, minimale (z.B. Alpine, Distroless) oder von Ihnen selbst gehärtete Basis-Images.
   - Vermeiden Sie Images mit unnötigen Tools oder Bibliotheken.
2. **Image-Scannen auf Schwachstellen (Vulnerability Scanning):**
   - Integrieren Sie Image-Scanner (z.B. Clair, Trivy, Anchore) in Ihre CI/CD-Pipeline, um bekannte Schwachstellen (CVEs) in Abhängigkeiten und im Betriebssystem zu identifizieren und zu beheben.
3. **Image-Signierung und -Verifizierung:**
   - Signieren Sie Ihre Images nach dem Build-Prozess und verifizieren Sie diese Signaturen beim Deployment, um sicherzustellen, dass nur unveränderte und autorisierte Images ausgeführt werden. (z.B. mit Notary, Cosign).
4. **Minimale Abhängigkeiten und Dateisystem:**
   - Installieren Sie nur das Nötigste im Container. Jede zusätzliche Software erhöht die Angriffsfläche.
   - Keine sensiblen Daten (wie SSH-Keys, API-Keys) im Image speichern.

---

## Sichere Pod-Konfiguration und Laufzeit

1. **Pod Security Standards (PSS) / Pod Security Admission (PSA) anwenden:**
    - Seit Kubernetes 1.25 ist PSA der Nachfolger von Pod Security Policies (PSP). Konfigurieren Sie Ihren Cluster so, dass er die PSS auf Namespace-Ebene durchsetzt (z.B. `restricted` oder `baseline`).
2. **Security Context konfigurieren (im Pod- oder Container-Spec):**
    - `runAsNonRoot: true`: Führen Sie den Container-Prozess als nicht-privilegierter Benutzer aus. Dies ist die wichtigste grundlegende Maßnahme.
    - `readOnlyRootFilesystem: true`: Machen Sie das Root-Dateisystem des Containers schreibgeschützt. Das erschwert einem Angreifer die Persistenz.
    - `allowPrivilegeEscalation: false`: Verhindern Sie, dass Prozesse im Container ihre Privilegien erhöhen können (z.B. über `setuid`/`setgid`).
    - `capabilities`:
        - `drop: ["ALL"]`: Entfernen Sie alle Standard-Linux-Fähigkeiten.
        - `add: [...]`: Fügen Sie nur die *absolut notwendigen* Fähigkeiten hinzu, z.B. `NET_BIND_SERVICE` für das Binden an Ports unter 1024.
    - `seccompProfile`: Nutzen Sie Seccomp-Profile, um die Systemaufrufe (syscalls) zu beschränken, die ein Container ausführen darf. Standardmäßig `RuntimeDefault` oder `Localhost` (falls Sie ein eigenes Profil haben).
    - `apparmorProfile` / `selinuxOptions`: Für eine noch tiefere Absicherung auf Kernel-Ebene können Sie AppArmor- oder SELinux-Profile verwenden, um den Zugriff von Prozessen auf Systemressourcen zu steuern.
3. **Ressourcenlimits definieren:**
    - Setzen Sie `requests` und `limits` für CPU und Memory. Dies schützt den Host und andere Pods vor DoS-Angriffen durch ressourcenhungrige Pods.
4. **Service Accounts und RBAC (Role-Based Access Control):**
    - Jeder Pod sollte einen dedizierten Service Account verwenden.
    - Weisen Sie diesem Service Account nur die *minimal notwendigen* Berechtigungen über ClusterRoles und RoleBindings zu (Least Privilege Principle). Vermeiden Sie die standardmäßige Verwendung des `default` Service Accounts.
5. **Keine Host-Namespaces verwenden:**
    - Vermeiden Sie die Verwendung von `hostNetwork: true`, `hostPID: true`, `hostIPC: true`. Diese Optionen koppeln den Pod zu stark an den Host und können Sicherheitslücken schaffen.
6. **Privilegierte Container vermeiden:**
    - Setzen Sie `privileged: false`. Ein privilegierter Container hat vollen Zugriff auf den Host-Kernel und alle Geräte, was ein enormes Sicherheitsrisiko darstellt.
7. **Sichere Images für Init-Container und Sidecars:**
    - Alle Sicherheitsmaßnahmen, die für den Hauptcontainer gelten, sollten auch für Init-Container und Sidecar-Container angewendet werden.

---

## Netzwerksicherheit

1. **Network Policies einsetzen:**
    - Definieren Sie strikte Netzwerkrichtlinien, die den Ingress (eingehenden) und Egress (ausgehenden) Datenverkehr für Pods genau regeln.
    - Legen Sie fest, welche Pods mit welchen anderen Pods oder externen Diensten kommunizieren dürfen. Standardmäßig sollte alles blockiert sein, und nur das Nötigste erlaubt werden (Default Deny).
2. **Mutual TLS (mTLS) zwischen Pods:**
    - Implementieren Sie mTLS, um sicherzustellen, dass nur authentifizierte Pods miteinander kommunizieren können. Dies ist oft Teil einer Service-Mesh-Lösung (z.B. Istio, Linkerd).
3. **Egress-Kontrolle:**
    - Beschränken Sie den ausgehenden Verkehr von Pods auf das absolute Minimum, um die Exfiltration von Daten oder die Kommunikation mit C2-Servern zu verhindern.
4. **Kein NodePort oder HostPort, wenn nicht unbedingt nötig:**
    - Verwenden Sie Ingress-Controller, Load Balancer oder andere Gateway-Lösungen, um den Zugriff von außen zu steuern, anstatt Ports direkt auf den Worker Nodes zu exponieren.

---

## Datenschutz und Geheimnisverwaltung

1. **Kubernetes Secrets mit KMS v2 (Encryption at Rest):**
    - Aktivieren Sie einen KMS-Provider im Kubernetes API-Server, um Secrets im etcd-Datenspeicher zu verschlüsseln. Dies schützt Secrets im Ruhezustand.
2. **Externes Secret Management System (z.B. HashiCorp Vault, AWS Secrets Manager, Azure Key Vault):**
    - Für höchste Sicherheit sollten sensible Daten (insbesondere private TLS-Schlüssel) nicht direkt in Kubernetes Secrets gespeichert werden, sondern in einem externen, gehärteten Secret Management System.
    - Der Pod sollte diese Secrets zur Laufzeit über einen Secret-Injektor (z.B. HashiCorp Vault Agent, CSI Secrets Store Driver) abrufen.
    - Idealerweise wird der private Schlüssel nur im Arbeitsspeicher gehalten und niemals auf die Festplatte geschrieben.
3. **Vermeiden Sie sensible Daten in Umgebungsvariablen:**
    - Umgebungsvariablen sind leicht auslesbar und werden oft in Logs oder beim Debugging sichtbar. Nutzen Sie stattdessen Secrets (gemountet als Datei) oder ein externes Secret Management System.
4. **Volumen-Sicherheit:**
    - Verwenden Sie verschlüsselte Persistent Volumes, wenn Sie sensible Daten speichern müssen.
    - Achten Sie auf korrekte Zugriffsrechte auf gemountete Volumes.

---

## Cluster- und Infrastruktur-Sicherheit (Wirkt sich auf Pods aus)

1. **Gehärtete Worker Nodes:**
    - Halten Sie das Betriebssystem der Worker Nodes aktuell.
    - Entfernen Sie unnötige Dienste und Software.
    - Implementieren Sie Host-Level-Firewalls.
    - Nutzen Sie Tools wie OSquery für Host-Level-Überwachung.
2. **Umfassendes RBAC für alle Benutzer:**
    - Definieren Sie strenge RBAC-Richtlinien für alle Benutzer und Gruppen, die mit dem Cluster interagieren (Entwickler, Operatoren, CI/CD-Systeme). Wenden Sie das Least Privilege Principle an.
3. **Audit-Logs aktivieren und überwachen:**
    - Konfigurieren Sie Kubernetes-Audit-Logs, um alle API-Aufrufe zu protokollieren.
    - Integrieren Sie diese Logs in ein SIEM (Security Information and Event Management) System zur Analyse und Alarmierung.
4. **Admission Controller nutzen:**
    - Verwenden Sie zusätzliche Admission Controller (z.B. OPA Gatekeeper, Kyverno), um Richtlinien durchzusetzen, die über PSS hinausgehen (z.B. nur signierte Images zulassen, bestimmte Labels oder Annotations erzwingen).
5. **Regelmäßige Updates des Kubernetes-Clusters:**
    - Halten Sie Ihren Kubernetes-Cluster und die verwendeten Komponenten (Kubelet, API-Server, etcd) aktuell, um von den neuesten Sicherheits-Fixes zu profitieren.

---

## Betriebliche und Prozessuale Maßnahmen

1. **Sichere CI/CD-Pipelines:**
    - Automatisieren Sie Sicherheitsprüfungen (Statische Code-Analyse, Dependency-Scanning, Image-Scanning) frühzeitig im Entwicklungsprozess.
    - Stellen Sie sicher, dass Ihre Build-Systeme selbst sicher sind.
2. **Regelmäßige Sicherheitsaudits und Penetration Tests:**
    - Lassen Sie Ihre Kubernetes-Infrastruktur und die darauf laufenden Anwendungen regelmäßig von unabhängigen Dritten auf Schwachstellen prüfen.
3. **Incident Response Plan:**
    - Entwickeln und üben Sie einen detaillierten Plan für den Fall einer Sicherheitsverletzung.
    - Stellen Sie sicher, dass Sie forensische Daten (Logs, Metriken) sammeln können.
4. **Schulung und Sensibilisierung:**
    - Schulen Sie Ihre Entwickler, Operatoren und alle relevanten Mitarbeiter regelmäßig in Kubernetes-Sicherheit und den besten Praktiken für die Arbeit mit Containern.
5. **Versionierung und Immutable Infrastructure:**
    - Verwalten Sie alle Pod-Definitionen und Kubernetes-Konfigurationen in der Versionskontrolle.
    - Behandeln Sie Ihre Pods als unveränderlich: Bei Änderungen werden Pods neu erstellt, nicht aktualisiert.

---

## Weiterführende Referenzen

- [OWASP Kubernetes Top Ten](https://owasp.org/www-project-kubernetes-top-ten/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Kubernetes Hardening Guide](https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes/)
- [Kubernetes Security Whitepaper](https://www.cncf.io/wp-content/uploads/2020/04/CNCF-Kubernetes-Security-Whitepaper.pdf)
- [Kubernetes Security Audit Tools](https://kubernetes.io/docs/tasks/administer-cluster/security-audit/)