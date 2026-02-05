#!/bin/bash

echo "Setting up Qwen LLM with Envoy AI Gateway and Token-based Rate Limiting..."

# 1. Install AI Gateway components
echo "Installing AI Gateway CRDs..."
helm upgrade -i aieg-crd oci://docker.io/envoyproxy/ai-gateway-crds-helm \
  --version v0.0.0-latest \
  --namespace envoy-ai-gateway-system \
  --create-namespace

echo "Installing AI Gateway Controller..."
helm upgrade -i aieg oci://docker.io/envoyproxy/ai-gateway-helm \
  --version v0.0.0-latest \
  --namespace envoy-ai-gateway-system \
  --create-namespace

# 2. Update Envoy Gateway with AI extensions
echo "Updating Envoy Gateway with AI extensions..."
helm upgrade -i eg oci://docker.io/envoyproxy/gateway-helm \
  --version v0.0.0-latest \
  --namespace envoy-gateway-system \
  --create-namespace \
  -f /home/nagesh/DevConf-2026/gateway/envoy-gateway-values.yaml

# 3. Apply rate limit configuration
echo "Applying rate limit configuration..."
kubectl apply -f /home/nagesh/DevConf-2026/gateway/ratelimit-config.yaml

# 4. Apply LLM gateway configuration
echo "Applying Qwen LLM gateway configuration..."
kubectl apply -f /home/nagesh/DevConf-2026/gateway/qwen-llm-gateway.yaml

# 5. Wait for pods to be ready
echo "Waiting for gateway pods to be ready..."
kubectl wait --timeout=300s --for=condition=Ready pods -l app.kubernetes.io/name=envoy-ratelimit -n envoy-gateway-system
kubectl wait --timeout=300s --for=condition=Ready pods -l app.kubernetes.io/name=gateway-helm -n envoy-gateway-system

echo "Setup complete!"
echo ""
echo "Test your LLM gateway:"
echo "1. Get gateway external IP:"
echo "   kubectl get svc -n envoy-gateway-system"
echo ""
echo "2. Test with Bearer token:"
echo "   curl -H 'Authorization: Bearer your-token' \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"model\":\"qwen2.5\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}' \\"
echo "        http://GATEWAY-IP/v1/chat/completions"
echo ""
echo "3. Test with API key:"
echo "   curl -H 'X-API-Key: your-api-key' \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"model\":\"qwen2.5\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}' \\"
echo "        http://GATEWAY-IP/v1/chat/completions"
