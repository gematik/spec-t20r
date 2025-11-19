#!/bin/bash

set -e

echo "🧪 Starting Tetragon Policy Tests..."
OVERALL_STATUS=0

# Function to check if a policy exists
check_policy() {
    local policy_name=$1
    if kubectl get tracingpolicy -n vsdm2 "$policy_name" &> /dev/null; then
        echo "✅ Policy '$policy_name' is loaded in vsdm2."
    else
        echo "❌ Policy '$policy_name' is NOT loaded in vsdm2."
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
# Start listening for logs in background with increased concurrency limit
kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f --tail=0 --max-log-requests=20 > envoy_logs.txt &
LOG_PID=$!

# Generate traffic
# Ensure curl-test-envoy doesn't exist from previous run
kubectl delete pod curl-test-envoy -n vsdm2 --ignore-not-found=true &> /dev/null
# Use correct service name and port (envoy-pep-svc on port 80)
# Remove -s -o /dev/null to see output on failure
echo "   Running curl..."
kubectl run curl-test-envoy -n vsdm2 --image=curlimages/curl --rm -it --restart=Never -- curl -v http://envoy-pep-svc.vsdm2.svc.cluster.local || true

# Wait a bit for logs to be flushed
sleep 5
kill $LOG_PID || true

if grep -q "process_kprobe" envoy_logs.txt && grep -q "tcp_connect" envoy_logs.txt && grep -q "/usr/local/bin/envoy" envoy_logs.txt; then
    echo "✅ Envoy tracing verified: Found 'tcp_connect' from '/usr/local/bin/envoy'."
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
echo "   Applying deny-curl policy in vsdm2..."
cat <<EOF | kubectl apply -f -
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: deny-curl
  namespace: vsdm2
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
        - "/bin/curl"
      matchActions:
      - action: Sigkill
EOF

echo "   Waiting for policy to be active..."
sleep 10

echo "   Attempting to run curl (should be killed)..."
# Ensure curl-test-deny doesn't exist
kubectl delete pod curl-test-deny -n vsdm2 --ignore-not-found=true &> /dev/null

set +e # Expect failure
# Run curl via sh -c to ensure execve is called for curl
kubectl run curl-test-deny -n vsdm2 --image=alpine --rm -it --restart=Never -- /bin/sh -c "apk add curl && curl google.com"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
    echo "✅ Enforcement verified: Curl command was killed/failed as expected."
else
    echo "❌ Enforcement FAILED: Curl command succeeded but should have been blocked."
    OVERALL_STATUS=1
fi

echo "   Cleaning up deny-curl policy..."
kubectl delete tracingpolicy deny-curl -n vsdm2

echo ""
if [ $OVERALL_STATUS -eq 0 ]; then
    echo "Verdict: PASSED"
    exit 0
else
    echo "Verdict: FAILED"
    exit 1
fi
