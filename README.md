# LLM Security Pipeline - Shift Left Implementation

## Overview
End-to-end security pipeline for LLMs with model signing, vulnerability scanning, guardrails, and API gateway management.

## Architecture
```
Client → Envoy Gateway (Rate Limit) → Guardrails (Input) → Model Service → Guardrails (Output) → Response
         ↓                              ↓                      ↓
    Redis Cache                    Jailbreak/Injection    MinIO Storage
                                   Harmful Content
```

**Detailed Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)

**Diagrams**:
- [Deployment Architecture](diagrams/deployment_architecture.puml) - Full minikube deployment
- [Request Flow](diagrams/request_flow.puml) - Request processing with security layers
- [Security Layers](diagrams/security_layers.puml) - Defense in depth visualization

## Components
1. **Model Fetch**: Pull models from HuggingFace
2. **Model Signing**: Cosign + Sigstore for authenticity
3. **Security Scanning**: NVIDIA Garak for vulnerability assessment
4. **Guardrails**: Pre/post filtering with monitoring
5. **API Gateway**: Envoy with rate limiting and service mesh
6. **Orchestration**: Kubeflow for ML pipeline management

## Target Models
- Qwen2.5-0.5B (with ASR capabilities)
- apple/OpenELM-450M
- google/gemma-2-2b-it
- microsoft/DialoGPT-medium (for testing)

## Current Deployment Status

### Minikube Cluster
- **Status**: Running
- **Components Deployed**:
  - ✅ KServe (Model Serving)
  - ✅ Kubeflow Pipelines
  - ✅ Cert-Manager
  - ✅ Envoy AI Gateway
  - ✅ MinIO (Model Storage)
  - ✅ MySQL (Metadata Store)
  
### Active Models
- `qwen-model` - Base Qwen model deployment
- `qwen-model-secure` - Secured Qwen model with guardrails

## Quick Start

### Minikube Setup (Kubernetes)
```bash
# Start minikube (if not running)
minikube start --cpus=4 --memory=8192 --disk-size=40g

# Deploy the pipeline
./scripts/setup.sh
./scripts/pipeline.sh
```

### Local Development (Docker)
```bash
./scripts/quick_start.sh
```

### Manual Steps
```bash
# 1. Setup environment
./scripts/setup.sh

# 2. Download models
python3 scripts/model_fetch.py

# 3. Sign models
python3 scripts/model_signing.py

# 4. Run security scans
python3 scripts/garak_scan.py

# 5. Setup guardrails
python3 scripts/setup_guardrails.py

# 6. Test pipeline
python3 scripts/test_pipeline.py
```

## Services

### Minikube Deployment
- **Envoy AI Gateway**: `minikube service envoy-ai-gateway -n kubeflow --url`
- **Kubeflow UI**: `kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80`
- **KServe Models**: 
  - qwen-model: `http://qwen-model-predictor.kubeflow.svc.cluster.local`
  - qwen-model-secure: `http://qwen-model-secure-predictor.kubeflow.svc.cluster.local`
- **MinIO**: `kubectl port-forward -n kubeflow svc/minio-service 9000:9000`

### Local Docker Deployment
- **Guardrails API**: http://localhost:8000
- **Model Service**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger Tracing**: http://localhost:16686

## Directory Structure
```
DevConf-2026/
├── scripts/                      # Pipeline automation scripts
│   ├── setup.sh                 # Main setup script
│   ├── pipeline.sh              # Pipeline execution
│   ├── qwen_security_pipeline.py # Security pipeline implementation
│   ├── serve_with_guardrails.py # Guardrails service
│   ├── verify-artifacts.sh      # Artifact verification
│   └── ...
├── configs/                     # Kubernetes configurations
├── gateway/                     # Envoy/Istio configurations
│   ├── envoy-ai-gateway.yaml   # Envoy gateway deployment
│   └── ...
├── kubeflow/                    # Kubeflow pipeline definitions
│   ├── qwen_security_pipeline.yaml
│   ├── kserve-qwen-minio.yaml
│   ├── kserve-qwen-secure.yaml
│   └── ...
├── monitoring/                  # Prometheus/Grafana configs
├── my-poc/                      # POC configurations
├── models/                      # Downloaded models (runtime)
├── security/                    # Signing keys and scan results (runtime)
└── docker-compose.yml           # Local development setup
```

## Security Features
- ✅ Model authenticity verification with Cosign
- ✅ Comprehensive vulnerability scanning with Garak
- ✅ Real-time content filtering (toxicity, PII, bias)
- ✅ Rate limiting and API protection
- ✅ Service mesh security with mTLS
- ✅ Monitoring and alerting
- ✅ Distributed tracing

## Testing & Verification

See [TESTING.md](TESTING.md) for comprehensive testing guide with results:
- ✅ Minikube cluster verification
- ✅ KServe inference service tests
- ✅ Envoy gateway functionality (rate limiting working)
- ✅ Guardrails configuration validation
- ⚠️ Model signature verification (pending upload)

## References
- [Sigstore Model Signing](https://next.redhat.com/2025/04/10/model-authenticity-and-transparency-with-sigstore/)
- [NVIDIA Garak](https://github.com/NVIDIA/garak)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [Envoy AI Gateway](https://aigateway.envoyproxy.io/)
