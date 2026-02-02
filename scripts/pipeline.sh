#!/bin/bash
set -e

echo "🚀 Starting LLM Security Pipeline..."

# Step 1: Model Fetch
echo "📥 Step 1: Fetching models from HuggingFace..."
python3 scripts/model_fetch.py

# Step 2: Model Signing
echo "🔐 Step 2: Signing models with Cosign..."
python3 scripts/model_signing.py

# Step 3: Security Scanning
echo "🔍 Step 3: Running Garak security scans..."
python3 scripts/garak_scan.py

# Step 4: Setup Guardrails
echo "🛡️ Step 4: Setting up guardrails..."
python3 scripts/setup_guardrails.py

# Step 5: Deploy Gateway (if Kubernetes is available)
if command -v kubectl &> /dev/null; then
    echo "🌐 Step 5: Deploying API Gateway..."
    
    # Check if Envoy Gateway is preferred
    if [[ "$1" == "envoy" ]]; then
        echo "Using Envoy Gateway..."
        kubectl apply -f gateway/envoy-gateway.yaml
    else
        echo "Using Istio Service Mesh..."
        kubectl apply -f gateway/istio-config.yaml
    fi
    
    # Deploy Kubeflow pipeline
    echo "🔄 Step 6: Deploying Kubeflow pipeline..."
    kubectl apply -f kubeflow/pipeline.yaml
else
    echo "⚠️ Kubernetes not available, skipping gateway deployment"
fi

echo "✅ LLM Security Pipeline setup complete!"
echo ""
echo "📊 Summary:"
echo "- Models downloaded and signed"
echo "- Security scans completed"
echo "- Guardrails configured"
echo "- API Gateway deployed (if K8s available)"
echo ""
echo "🔧 Next steps:"
echo "1. Start guardrails service: python guardrails/service.py"
echo "2. Review security scan results in security/garak_results.json"
echo "3. Configure monitoring and alerting"
echo "4. Test the complete pipeline"
