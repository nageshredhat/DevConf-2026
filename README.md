# LLM Security Pipeline - Shift Left Implementation

## Overview
End-to-end security pipeline for LLMs with model signing, vulnerability scanning, guardrails, and API gateway management.

## Architecture
```
Model Registry (HuggingFace) → Cosign/Sigstore → NVIDIA Garak → Guardrails → Envoy Gateway → Kubeflow
```

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

## Quick Start

### Local Development (Docker)
```bash
./scripts/quick_start.sh
```

### Full Pipeline (Kubernetes)
```bash
./scripts/setup.sh
./scripts/pipeline.sh
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
- **Guardrails API**: http://localhost:8000
- **Model Service**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger Tracing**: http://localhost:16686

## Directory Structure
```
DevConf/
├── scripts/           # Pipeline automation scripts
├── configs/           # Kubernetes configurations
├── gateway/           # Envoy/Istio configurations
├── guardrails/        # Guardrails service code
├── kubeflow/          # Kubeflow pipeline definitions
├── monitoring/        # Prometheus/Grafana configs
├── models/            # Downloaded models (created at runtime)
├── security/          # Signing keys and scan results
└── docker-compose.yml # Local development setup
```

## Security Features
- ✅ Model authenticity verification with Cosign
- ✅ Comprehensive vulnerability scanning with Garak
- ✅ Real-time content filtering (toxicity, PII, bias)
- ✅ Rate limiting and API protection
- ✅ Service mesh security with mTLS
- ✅ Monitoring and alerting
- ✅ Distributed tracing

## References
- [Sigstore Model Signing](https://next.redhat.com/2025/04/10/model-authenticity-and-transparency-with-sigstore/)
- [NVIDIA Garak](https://github.com/NVIDIA/garak)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [Envoy AI Gateway](https://aigateway.envoyproxy.io/)
