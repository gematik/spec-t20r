#!/bin/bash

set -e

echo "🧪 Starting Tetragon Policy Tests..."
OVERALL_STATUS=0

# Function to check if a policy exists
check_policy() {
    POLICY_NAME=$1
    NAMESPACE=$2
    if kubectl get tracingpolicynamespaced -n $NAMESPACE $POLICY_NAME &> /dev/null; then
        echo "✅ Policy '$POLICY_NAME' is loaded in $NAMESPACE."
    else
        echo "❌ Policy '$POLICY_NAME' is NOT loaded in $NAMESPACE."
        OVERALL_STATUS=1
    fi
}

# 1. Verify Policies are Loaded
echo ""
echo "📋 Test Case 1: Verifying Policies are Loaded..."
check_policy "envoy-tracing"
check_policy "opa-tracing"
check_policy "otel-tracing"

# 2. Verify Envoy Tracing
echo ""
echo "📋 Test Case 2: Verifying Envoy Tracing..."
echo "   Generating traffic..."
# Restart Envoy to ensure new connections (avoid keep-alive reuse)
kubectl rollout restart deployment -n vsdm2 envoy-pep
kubectl rollout status deployment -n vsdm2 envoy-pep --timeout=60s

# Start listening for logs in background with increased concurrency limit
kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f --tail=0 --max-log-requests=20 > envoy_logs.txt &
LOG_PID=$!

# Generate traffic
# Ensure curl-test-envoy doesn't exist from previous run
kubectl delete pod curl-test-envoy -n vsdm2 --ignore-not-found=true &> /dev/null
# Use correct service name and port (envoy-pep-svc on port 80) with a valid path to trigger forwarding
# Remove -s -o /dev/null to see output on failure
echo "   Running curl..."
kubectl run curl-test-envoy -n vsdm2 --image=curlimages/curl --rm -it --restart=Never -- curl -v http://envoy-pep-svc.vsdm2.svc.cluster.local/vsdservice/v1/vsdmbundle || true

# Wait a bit for logs to be flushed
sleep 5
kill $LOG_PID || true

if grep -q "process_kprobe" envoy_logs.txt && (grep -q "tcp_connect" envoy_logs.txt || grep -q "sys_socket" envoy_logs.txt || grep -q "sys_connect" envoy_logs.txt); then
    echo "✅ Envoy tracing verified: Found 'tcp_connect', 'sys_connect', or 'sys_socket' from Envoy."
else
    echo "❌ Envoy tracing NOT verified."
    echo "   --- envoy_logs.txt content ---"
    cat envoy_logs.txt
    echo "   ------------------------------"
    OVERALL_STATUS=1
fi
rm envoy_logs.txt

# 3. Verify Otel Collector Tracing
echo ""
echo "📋 Test Case 3: Verifying Otel Collector Tracing..."
echo "   Restarting Otel Collector to trigger socket events..."
# Start listening for logs
kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f --tail=0 --max-log-requests=20 > otel_logs.txt &
LOG_PID=$!

# Restart deployment instead of deleting pod to avoid race conditions
kubectl rollout restart deployment -n vsdm2 otel-collector
# Wait for rollout to finish
kubectl rollout status deployment -n vsdm2 otel-collector --timeout=60s

sleep 10
kill $LOG_PID || true

if grep -q "process_kprobe" otel_logs.txt && grep -q "sys_socket" otel_logs.txt && grep -q "/otelcol-contrib" otel_logs.txt; then
    echo "✅ Otel tracing verified: Found 'sys_socket' from '/otelcol-contrib'."
else
    echo "❌ Otel tracing NOT verified."
    echo "   --- otel_logs.txt content ---"
    cat otel_logs.txt
    echo "   -----------------------------"
    OVERALL_STATUS=1
fi
rm otel_logs.txt

# 4. Verify Enforcement (Demo)
echo ""
echo "📋 Test Case 4: Verifying Enforcement (Demo)..."
echo "   Applying deny-curl policy globally..."
cat <<EOF | kubectl apply -f -
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
    - matchArgs:
      - index: 0
        operator: "Equal"
        values:
        - "/usr/bin/curl"
      matchActions:
      - action: Sigkill
EOF

echo "   Waiting for policy to be active..."
sleep 20

# Verify policy is loaded
if kubectl get tracingpolicy deny-curl &> /dev/null; then
    echo "   ✓ Policy 'deny-curl' confirmed loaded"
else
    echo "   ✗ Policy 'deny-curl' failed to load"
    OVERALL_STATUS=1
fi

echo "   Attempting to run curl (should be killed)..."
# Ensure curl-test-deny doesn't exist
kubectl delete pod curl-test-deny -n vsdm2 --ignore-not-found=true &> /dev/null

set +e # Expect failure
# Run curl using curlimages/curl without --rm so we can check status later
kubectl run curl-test-deny -n vsdm2 --image=curlimages/curl --restart=Never -- curl -v google.com
RET=$?
set -e

# Wait for pod to complete
echo "   Waiting for pod to complete..."
sleep 10

# Find the node where the pod ran
NODE_NAME=$(kubectl get pod curl-test-deny -n vsdm2 -o jsonpath='{.spec.nodeName}')
echo "   Pod ran on node: $NODE_NAME"

# Find the Tetragon pod on that node
TETRAGON_POD=$(kubectl get pods -n kube-system -l app.kubernetes.io/name=tetragon --field-selector spec.nodeName=$NODE_NAME -o jsonpath='{.items[0].metadata.name}')
echo "   Tetragon agent on node: $TETRAGON_POD"

# Check pod exit code
POD_EXIT_CODE=$(kubectl get pod curl-test-deny -n vsdm2 -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}' 2>/dev/null || echo "unknown")
echo "   Pod exit code: $POD_EXIT_CODE"

# Fetch logs from that specific Tetragon pod
kubectl logs -n kube-system $TETRAGON_POD -c export-stdout --tail=200 > enforcement_logs.txt

# Check for SIGKILL (exit code 137) or Sigkill action in logs
if [ "$POD_EXIT_CODE" = "137" ] || grep -q "Sigkill" enforcement_logs.txt; then
    echo "✅ Enforcement verified: Curl was killed by Tetragon (exit code: $POD_EXIT_CODE)."
else
    echo "❌ Enforcement FAILED: Curl command was not blocked."
    echo "   Pod exit code: $POD_EXIT_CODE (expected 137 for SIGKILL)"
    echo "   --- enforcement_logs.txt content (filtered for curl) ---"
    grep "curl" enforcement_logs.txt | head -n 20
    echo "   --------------------------------------------------------"
    OVERALL_STATUS=1
fi

echo "   Cleaning up deny-curl policy and pod..."
kubectl delete tracingpolicy deny-curl
kubectl delete pod curl-test-deny -n vsdm2 --ignore-not-found=true
rm enforcement_logs.txt || true

echo ""
if [ $OVERALL_STATUS -eq 0 ]; then
    echo "Verdict: PASSED"
    exit 0
else
    echo "Verdict: FAILED"
    exit 1
fi
