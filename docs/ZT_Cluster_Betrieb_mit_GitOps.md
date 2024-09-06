# Betrieb des ZT Cluster mit GitOps

## Was ist  GitOps CD?

GitOps ist eine Methode zur Verwaltung von Anwendungen und Infrastruktur in Kubernetes-Clustern, bei der Git als Single Source of Truth für die gesamte Konfiguration dient. GitOps basiert auf den folgenden Prinzipien:

- **Deklarative Konfiguration**: Die gesamte Konfiguration der Anwendungen und Infrastruktur wird in Git-Repositories als Code gespeichert. Dieser Code definiert den gewünschten Zustand des Clusters.
- **Automatisierte Synchronisierung**: Ein GitOps-Tool (z.B. ArgoCD, Flux) überwacht kontinuierlich das Git-Repository und stellt sicher, dass der Kubernetes-Cluster immer den gewünschten Zustand widerspiegelt. Änderungen an der Konfiguration werden automatisch angewendet.
- **Versionierung und Rückverfolgbarkeit**: Jede Änderung an der Konfiguration wird als Commit im Git-Repository gespeichert, was eine vollständige Versionierung und Historie aller Änderungen ermöglicht. Es ist möglich, zu früheren Versionen zurückzukehren.

## Wer macht was im ZT Cluster GitOps CD Prozess?

- **Entwicklung der Docker Images** Die Entwicklung aller Docker Images des ZT Clusters sowie aller Testkomponenten und Testfälle erfolgt durch den **Hersteller Zero Trust** (Auftragnehmer der Zero Trust Ausschreibung). Zusätzlich werden Kubernetes (K8s) Manifeste für eine ZT Cluster Konfiguration sowie Terraform Scripte für ein automatisches Deployment als Templates bereitgestellt. Alle Artefakte werden in einem CI Prozess qualitätsgesichert und in einem git Repository der Gematik bereitgestellt.
- **Bereitstellung signierter Docker Images** In einer Container-Registry der **gematik** werden die Docker Images signiert und bereitgestellt.
- **Spezifische ZT Cluster Konfiguration für einen TI 2.0 Dienst** Jeder TI 2.0 Dienst hat spezifische Anforderungen an die Verfügbarkeit, Performance, Lastverhalten und verwendete Infrastruktur. Daher kann nur der **Betreiber eines TI 2.0 Dienstes** die Konfiguration (K8s Manifest Dateien) des ZT Clusters erstellen. Der Betreiber eines TI 2.0 Dienstes trägt die Betriebsverantwortung für seinen Dienst inklusive ZT Cluster. Die Konfiguration des ZT Clusters wird in einem eigenen Prozess des Betreibers qualitätsgesichert. Der Betreiber verwendet eigene Deployments und ggf. Referenz-Instanzen anderer Dienste um seine Tests durchzuführen. Nach Fertigstellung der Konfiguration wird sie in ein git Repository der Gematik kopiert. Der Betreiber des TI 2.0 Dienstes stellt einen Changs-Request, um eine Freigabe für die geänderte ZT Cluster Konfiguration zu erhalten.
- **Konsistenzprüfung der ZT Cluster Konfiguration** Die **gematik** prüft zusätzlich zum Betreiber des TI 2.0 Dienstes die Konsistenz der ZT Cluster Konfiguration und führt automatisierte Prüfungen der Konfiguration durch. Die Prüfung umfasst die Validierung der K8s Manifeste, die Prüfung auf Konformität mit den gematik Vorgaben und die Prüfung auf Sicherheitsaspekte. Bei erfolgreicher Prüfung wird die Konfiguration in ein Verzeichnis übernommen, aus dem der Cluster Management Service des ZT Clusters die Manifest-Dateien bezieht. Das git Repository der gematik wird so betrieben, dass es auch für einen Admin nicht möglich ist, allein die Konfiguration direkt zu ändern. Jede Änderung ist über git Mechanismen nachvollziehbar und kann rückgängig gemacht werden. Es können verschiedene Umgebungen (z.B. Test, Staging, Produktion) durch unterschiedliche Branches oder Tags abgebildet werden.
- **Deployment der ZT Cluster Konfiguration** Die Übernahme der ZT Cluster Konfiguration in den ZT Cluster erfolgt durch den **Cluster-Management Service** des ZT Clusters. Der Cluster-Management Service übernimmt die Konfiguration aus dem git Repository und wendet sie im ZT Cluster an. Der Cluster-Management Service überwacht den Zustand des ZT Clusters und führt bei Bedarf Anpassungen durch und verhindert Änderungen durch lokale Administratoren.

## Begründung für GitOps

GitOps ist eine besonders effektive Methode zur Verwaltung und Bereitstellung von Anwendungen und Infrastruktur in Kubernetes-Clustern. Im Vergleich zu traditionellen Betriebsmethoden bietet GitOps mehrere Vorteile:

### 1. **Versionierung und Rückverfolgbarkeit**
   - **Zentrale Quelle der Wahrheit**: Git dient als Single Source of Truth für die gesamte Infrastruktur und Anwendungen. Jede Änderung wird als Commit in einem Git-Repository gespeichert, was eine vollständige Versionierung und Historie aller Änderungen ermöglicht.
   - **Einfache Rückkehr zu vorherigen Versionen**: Bei Problemen kann man einfach zu einer vorherigen Version des Clusters oder der Anwendung zurückkehren, indem man einen früheren Commit auscheckt.

### 2. **Automatisierung und Konsistenz**
   - **Automatische Synchronisierung**: GitOps-Tools wie ArgoCD oder Flux beobachten kontinuierlich das Git-Repository und stellen sicher, dass der Kubernetes-Cluster immer den gewünschten Zustand widerspiegelt, wie er im Repository definiert ist.
   - **Minimierung von menschlichen Fehlern**: Da Änderungen an der Infrastruktur und den Anwendungen über Pull-Requests und automatisierte Pipelines abgewickelt werden, wird die Wahrscheinlichkeit menschlicher Fehler deutlich reduziert.

### 3. **Transparenz und Zusammenarbeit**
   - **Nachvollziehbare Änderungen**: Änderungen werden durch Pull-Requests oder Merge-Requests vorgenommen, die von anderen Teammitgliedern überprüft werden können. Dies fördert die Zusammenarbeit und sorgt für Transparenz.
   - **Audit-Trails**: Jede Änderung ist dokumentiert und nachverfolgbar, was insbesondere für Compliance-Zwecke nützlich ist.

### 4. **Schnellere und sicherere Bereitstellung**
   - **Kontinuierliche Bereitstellung**: GitOps ermöglicht kontinuierliche Bereitstellung (Continuous Deployment) durch den Einsatz von CI/CD-Pipelines, die auf jedes Commit reagieren und den Kubernetes-Cluster automatisch aktualisieren.
   - **Sicherheitsmechanismen**: Durch die Nutzung von Git für das Management können Sicherheitsprüfungen (z.B. Code-Reviews) vor der Anwendung von Änderungen durchgeführt werden, was die Sicherheit der Umgebung erhöht.

### 5. **Skalierbarkeit und Reproduzierbarkeit**
   - **Einfaches Skalieren von Umgebungen**: Da die gesamte Infrastruktur als Code im Git-Repository gespeichert ist, können Umgebungen einfach repliziert oder skaliert werden, indem man die entsprechenden Konfigurationen in neue Cluster überträgt.
   - **Reproduzierbarkeit**: Die gesamte Infrastruktur und Anwendungen können in beliebigen Umgebungen konsistent reproduziert werden, was für Tests und Entwicklung nützlich ist.

### 6. **Integration von Infrastruktur und Anwendung**
   - **Gemeinsame Verwaltung**: Sowohl die Anwendung als auch die Infrastruktur, auf der sie läuft, können im gleichen Git-Repository verwaltet werden. Dies erleichtert das Management der gesamten Umgebung und fördert die Konsistenz zwischen beiden Bereichen.

### Vergleich zu alternativen Methoden
   - **Manuelle Verwaltung**: Erhöht das Risiko menschlicher Fehler und macht es schwieriger, Änderungen nachzuverfolgen.
   - **Skripting- oder CI/CD-Pipelines ohne GitOps**: Bietet zwar Automatisierung, jedoch fehlt oft die klare Trennung zwischen gewünschtem Zustand (definiert im Code) und aktuellem Zustand im Cluster. Zudem gibt es oft keine integrierte Versionierung und Nachverfolgbarkeit der Infrastruktur.
   - **Konfigurationsmanagement-Tools (z.B. Ansible, Chef, Puppet)**: Diese bieten Automatisierung, sind jedoch oft nicht so eng mit Kubernetes integriert und bieten nicht die gleiche nahtlose Erfahrung für Kubernetes-spezifische Aufgaben.

Insgesamt ist GitOps eine ideale Methode für den Betrieb von Kubernetes-Clustern, da es Automatisierung, Versionierung, Sicherheit und Zusammenarbeit auf eine Weise kombiniert, die alternative Methoden oft nicht erreichen.
