#!/bin/bash

# Install AI Gateway CRDs
helm upgrade -i aieg-crd oci://docker.io/envoyproxy/ai-gateway-crds-helm \
  --version v0.0.0-latest \
  --namespace envoy-ai-gateway-system \
  --create-namespace

# Install AI Gateway Controller
helm upgrade -i aieg oci://docker.io/envoyproxy/ai-gateway-helm \
  --version v0.0.0-latest \
  --namespace envoy-ai-gateway-system \
  --create-namespace

# Install/Upgrade Envoy Gateway with AI extensions
helm upgrade -i eg oci://docker.io/envoyproxy/gateway-helm \
  --version v0.0.0-latest \
  --namespace envoy-gateway-system \
  --create-namespace \
  -f /home/nagesh/DevConf-2026/gateway/envoy-gateway-values.yaml

# Apply the gateway resources
kubectl apply -f /home/nagesh/DevConf-2026/gateway/envoy-gateway.yaml
