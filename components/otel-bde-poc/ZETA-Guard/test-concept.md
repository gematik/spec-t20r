# Tetragon Test Concept & Test Cases

## 1. Concept
The goal is to verify that the installed Tetragon policies are active and functioning correctly.
We will verify this in two ways:
1.  **Status Check**: Confirm policies are loaded by the Kubernetes API.
2.  **Functional Testing**: Trigger events that match the policies and verify they are logged (or blocked) by Tetragon.

## 2. Prerequisites
-   Cluster is running.
-   Tetragon is installed.
-   `kubectl` is configured.
-   Terminal access to run commands.

## 3. Test Cases

### Test Case 1: Verify Policies are Loaded
**Objective**: Ensure all TracingPolicies are accepted by the cluster.
**Command**:
```bash
kubectl get tracingpolicies
```
**Expected Result**:
-   `envoy-tracing`, `opa-tracing`, `otel-tracing` are listed.
-   Status (if available) shows enabled.

---

### Test Case 2: Verify Envoy Tracing (Network Activity)
**Objective**: Verify that `tcp_connect` events from Envoy are traced.
**Steps**:
1.  Start watching Tetragon logs in one terminal:
    ```bash
    kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f | grep "envoy"
    ```
2.  Generate traffic through Envoy (e.g., access the application):
    ```bash
    # In another terminal
    curl -v http://localhost/vsdservice/v1/vsdmbundle
    # Or if port forwarding is not active, just curl the pod IP or service from a temporary pod
    kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- curl -v http://envoy.vsdm2.svc.cluster.local:8080
    ```
**Expected Result**:
-   The log stream should show JSON events containing `process_kprobe` for `tcp_connect` initiated by `/usr/local/bin/envoy`.

---

### Test Case 3: Verify Otel Collector Tracing (Socket Activity)
**Objective**: Verify that `sys_socket` events from Otel Collector are traced.
**Steps**:
1.  Start watching Tetragon logs:
    ```bash
    kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f | grep "otelcol-contrib"
    ```
2.  Restart the Otel Collector pod to trigger socket creation during startup:
    ```bash
    kubectl delete pod -n vsdm2 -l app=otel-collector
    ```
**Expected Result**:
-   As the new pod starts, the log stream should show `process_kprobe` events for `sys_socket` initiated by `/otelcol-contrib`.

---

### Test Case 4: Verify OPA Enforcement (Security Rule)
**Objective**: Verify the OPA rule.
**Note**: The OPA policy `opa-tracing` is a **security enforcement rule** configured to `Sigkill` (kill) the process if `/opa` attempts to execute another binary (`sys_execve`).
**Verification Challenge**: Under normal operation, OPA does *not* execute other binaries. Triggering this requires an exploit or a modified OPA image.
**Alternative Verification**: To prove Tetragon *can* enforce this, we can temporarily deploy a "Test Pod" with a similar rule that we *can* trigger.

#### Optional: Enforcement Capability Test
1.  Create a test policy that kills `curl` commands.
    ```yaml
    apiVersion: cilium.io/v1alpha1
    kind: TracingPolicy
    metadata:
      name: deny-curl
    spec:
      kprobes:
      - call: "sys_execve"
        syscall: true
        args:
        - index: 0
          type: "string"
        selectors:
        - matchBinaries:
          - operator: "In"
            values:
            - "/usr/bin/curl"
          matchActions:
          - action: Sigkill
    ```
2.  Apply it: `kubectl apply -f deny-curl.yaml`
3.  Run a pod and try to curl: `kubectl run test-curl --image=curlimages/curl --rm -it --restart=Never -- curl google.com`
4.  **Expected**: The command should be killed immediately.
