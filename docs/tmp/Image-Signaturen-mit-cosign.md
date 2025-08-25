# Image-Signaturen mit Cosign

Das client-seitige Verifizierungs-Muster (auch "pre-flight check" genannt) ist die fortschrittlichste und performanteste Methode um Container zu signieren und die Signaturen zu verifizieren. Es verlagert die "teure" Arbeit der kryptographischen Verifizierung aus dem kritischen Pfad der Pod-Erstellung in die CI-Pipeline.

Hier ist ein detaillierter Ablauf, der Ihre Anforderungen an eine zweistufige Signatur (Entwickler und Maintainer) berücksichtigt.

## Vorbereitung: Die Bausteine im Cluster

Bevor die Pipelines laufen, müssen Sie zwei Dinge im Kubernetes-Cluster einrichten:

1. **Installation des Sigstore Policy CRD:**
    Sie müssen eine Custom Resource Definition (CRD) im Cluster installieren, die als "Beweis" oder "Attestierung" für ein verifiziertes Image dient. Die `ClusterImagePolicy` von Sigstore ist hierfür perfekt geeignet.

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/sigstore/policy-controller/main/config/crd/clusterimagepolicies.sigstore.dev.yaml
    ```

2. **Installation und Konfiguration von Kyverno:**
    Installieren Sie Kyverno in Ihrem Cluster. Danach erstellen Sie zwei Policies, die auf die Existenz der `ClusterImagePolicy`-Objekte prüfen – eine für Entwicklungs-Namespaces und eine für Produktions-Namespaces. (Die genauen Policies finden Sie am Ende dieses Ablaufs).

---

## Ablauf 1: Die Entwickler-CI-Pipeline

Diese Pipeline läuft bei jedem Commit oder Merge in einen Entwicklungs-Branch. Ihr Ziel ist es, ein Image zu bauen, es mit der Entwickler-Identität zu signieren und ein `ClusterImagePolicy`-Objekt zu erstellen, das dieses Image für die Entwicklungsumgebung freigibt.

**Trigger:** `git push` auf einen `feature/*` oder `develop` Branch.

**Schritte:**

1. **Code auschecken, bauen & pushen:**
    * Die Pipeline checkt den Code aus.
    * Ein Container-Image wird gebaut (z.B. mit Docker oder Kaniko).
    * Das Image wird in Ihre Container Registry gepusht, z.B. `registry.zeta.corp/zeta-guard:feature-abc-a1b2c3d`.
    * **Wichtig:** Die Pipeline muss den exakten Image-Digest (`sha256:...`) des gepushten Images erfassen.

    ```bash
    # Beispiel mit Docker
    IMAGE_TAG="registry.zeta.corp/zeta-guard:feature-abc-a1b2c3d"
    docker build . -t $IMAGE_TAG
    docker push $IMAGE_TAG
    IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE_TAG)
    echo "Image Digest ist: $IMAGE_DIGEST"
    ```

2. **Image mit Entwickler-Identität signieren:**
    * Die Pipeline nutzt `cosign`, um das Image mit der Identität des CI/CD-Jobs zu signieren (keyless signing). Diese Identität repräsentiert die "Entwickler-Signatur".

    ```bash
    # Annahme: Läuft in GitHub Actions oder GitLab CI mit OIDC-Konfiguration
    cosign sign --yes $IMAGE_DIGEST
    ```

    * Diese Signatur wird von `cosign` in der Registry gespeichert und im öffentlichen Rekor-Transparenzprotokoll eingetragen.

3. **Verifizieren & Kubernetes-Objekt erstellen:**
    * Dies ist der Kern des Musters. Die Pipeline verifiziert ihre *eigene* Signatur, um sicherzustellen, dass alles korrekt ist.
    * Wenn die Verifizierung erfolgreich ist, wird die `ClusterImagePolicy`-YAML-Datei generiert und auf den Cluster angewendet.

    ```bash
    # Schritt 3a: Eigene Signatur verifizieren
    # Wir geben die erwartete Identität des CI-Jobs an.
    # Dies stellt sicher, dass NUR unsere Entwickler-Pipeline signiert hat.
    cosign verify \
      --certificate-identity-regexp "https://github.com/zeta-corp/zeta-guard/.github/workflows/developer-ci.yml@refs/heads/develop" \
      --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
      $IMAGE_DIGEST

    # Wenn der obige Befehl erfolgreich war (exit code 0), geht es weiter.

    # Schritt 3b: ClusterImagePolicy YAML generieren
    # Der Name des Objekts sollte eindeutig sein, z.B. aus dem SHA-Hash des Digests.
    CIP_NAME=$(echo $IMAGE_DIGEST | sha256sum | awk '{print $1}')

    cat <<EOF > cip-developer.yaml
    apiVersion: sigstore.dev/v1alpha1
    kind: ClusterImagePolicy
    metadata:
      name: $CIP_NAME
      # Dieses Label ist entscheidend für die spätere Policy-Prüfung!
      labels:
        verification-level: "developer"
    spec:
      images:
      - glob: "${IMAGE_DIGEST}"
      authorities:
      - keyless:
          # Hier definieren wir, was eine GÜLTIGE Entwickler-Signatur ist.
          identities:
          - issuerRegexp: "https://token.actions.githubusercontent.com"
            subjectRegexp: "https://github.com/zeta-corp/zeta-guard/.*"
    EOF

    # Schritt 3c: Objekt im Kubernetes Cluster anwenden
    kubectl apply -f cip-developer.yaml
    ```

**Ergebnis:** Es existiert nun ein Objekt im Cluster, das kryptographisch bezeugt: "Das Image mit dem Digest `sha256:...` wurde von einer verifizierten Entwickler-Pipeline signiert." Andere Entwickler können dieses Image jetzt in ihren Entwicklungs-Namespaces verwenden.

---

## Ablauf 2: Die Maintainer-CI-Pipeline (General Availability)

Diese Pipeline wird nur ausgelöst, wenn ein Image als "GA" markiert wird, z.B. durch das Erstellen eines Git-Tags.

**Trigger:** `git tag -a v1.2.3` und `git push --tags`.

**Schritte:**

1. **Image identifizieren:**
    * Die Pipeline identifiziert den Image-Digest, der zu diesem Git-Tag gehört (z.B. aus einem Build-Manifest oder indem das Image neu gebaut und der Digest verglichen wird).

2. **Image mit Maintainer-Identität ZUSÄTZLICH signieren:**
    * Diese Pipeline läuft mit einer anderen Service-Account-Identität (z.B. `release-maintainer-ci.yml`), die die "Maintainer"-Rolle repräsentiert.
    * `cosign` fügt dem Image eine *zweite* Signatur hinzu. Die erste (Entwickler-)Signatur bleibt erhalten.

    ```bash
    # Läuft mit der Identität der Maintainer-Pipeline
    IMAGE_DIGEST="registry.zeta.corp/zeta-guard@sha256:..." # Digest aus Schritt 1
    cosign sign --yes $IMAGE_DIGEST
    ```

3. **Bestehendes Kubernetes-Objekt aktualisieren:**
    * Statt ein neues Objekt zu erstellen, wird das bereits existierende `ClusterImagePolicy`-Objekt der Entwickler-Pipeline **aktualisiert**, um den neuen, höheren Vertrauensstatus widerzuspiegeln.

    ```bash
    # Schritt 3a: Bestehendes Objekt finden und herunterladen
    CIP_NAME=$(echo $IMAGE_DIGEST | sha256sum | awk '{print $1}')
    kubectl get clusterimagepolicy $CIP_NAME -o yaml > cip-existing.yaml

    # Schritt 3b: Objekt modifizieren
    # Wir ändern das Label und fügen eine zweite Autorität hinzu.
    # Dies kann mit Tools wie 'yq' oder 'sed' in der Pipeline erfolgen.
    # Beispiel mit yq:
    yq e '.metadata.labels.["verification-level"] = "production"' -i cip-existing.yaml
    yq e '.spec.authorities += [{"keyless": {"identities": [{"issuerRegexp": "https://token.actions.githubusercontent.com", "subjectRegexp": "https://github.com/zeta-corp/zeta-guard/.github/workflows/maintainer-ci.yml@refs/tags/v.*"}]}}]' -i cip-existing.yaml

    # Schritt 3c: Aktualisiertes Objekt im Cluster anwenden
    kubectl apply -f cip-existing.yaml
    ```

**Ergebnis:** Das `ClusterImagePolicy`-Objekt für diesen Image-Digest hat jetzt das Label `verification-level: production` und erfordert in seiner Spezifikation zwei gültige Signaturen (Entwickler UND Maintainer).

---

## Erzwingung durch Kyverno (Der PEP)

Kyverno prüft nun bei jeder Pod-Erstellung extrem schnell und ressourcenschonend, ob der passende "Beweis" im Cluster existiert.

### Policy 1: Für Entwicklungs-Namespaces

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-developer-image-attestation
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: require-developer-level-verification
      match:
        any:
        - resources:
            kinds:
              - Pod
            # Gilt für alle Namespaces, die auf -dev oder -test enden
            namespaceSelector:
              matchExpressions:
                - key: "kubernetes.io/metadata.name"
                  operator: "In"
                  values: ["*-dev", "*-test"]
      validate:
        message: "Image {{image}} is not attested for developer use."
        # Für jedes Container-Image im Pod...
        foreach:
          - list: "request.object.spec.containers"
            # ...führe eine Abfrage an die K8s API durch
            apiCall:
              urlPath: "/apis/sigstore.dev/v1alpha1/clusterimagepolicies"
              jmesPath: "items[?spec.images[?glob=='{{element.image}}'] && metadata.labels.\"verification-level\"=='developer'] | length(@)"
            # ...und stelle sicher, dass mindestens ein Objekt gefunden wurde (> 0)
            deny:
              conditions:
                any:
                - key: "{{apiCall.result}}"
                  operator: "NotEquals"
                  value: 1
```

### Policy 2: Für Produktions-Namespaces

Diese Policy ist fast identisch, fragt aber nach dem `production`-Label.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-production-image-attestation
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: require-production-level-verification
      match:
        any:
        - resources:
            kinds:
              - Pod
            namespaceSelector:
              matchExpressions:
                - key: "kubernetes.io/metadata.name"
                  operator: "In"
                  values: ["prod", "ga", "zeta-system"]
      validate:
        message: "Image {{image}} is not attested for PRODUCTION use."
        foreach:
          - list: "request.object.spec.containers"
            apiCall:
              urlPath: "/apis/sigstore.dev/v1alpha1/clusterimagepolicies"
              # Der einzige Unterschied ist hier das Label
              jmesPath: "items[?spec.images[?glob=='{{element.image}}'] && metadata.labels.\"verification-level\"=='production'] | length(@)"
            deny:
              conditions:
                any:
                - key: "{{apiCall.result}}"
                  operator: "NotEquals"
                  value: 1
```

## Zusammenfassung der Vorteile dieses Musters

* **Extrem performant:** Kyverno führt nur eine schnelle, interne K8s-API-Abfrage durch. Keine Latenz durch externe Netzwerkaufrufe bei der Pod-Erstellung.
* **Ressourcenschonend:** Die kryptographische Last liegt ausschließlich in der CI-Pipeline, nicht auf dem K8s API-Server oder den Admission-Controllern.
* **Klare Trennung:** Die CI-Pipelines sind für die Erstellung der "Beweise" zuständig. Kyverno ist nur für die schnelle "Prüfung der Beweise" zuständig.
* **GitOps-freundlich:** Die `ClusterImagePolicy`-Objekte können wie jeder andere Kubernetes-Manifest in einem Git-Repository verwaltet werden, was volle Nachvollziehbarkeit bietet.