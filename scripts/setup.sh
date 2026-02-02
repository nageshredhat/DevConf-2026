#!/bin/bash
set -e

echo "Setting up LLM Security Pipeline..."

# Create directory structure
mkdir -p {scripts,configs,models,security,guardrails,gateway,monitoring}

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -q transformers torch huggingface_hub garak guardrails-ai

# Install cosign
echo "Installing cosign..."
if ! command -v cosign &> /dev/null; then
    curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-darwin-amd64"
    sudo mv cosign-darwin-amd64 /usr/local/bin/cosign
    sudo chmod +x /usr/local/bin/cosign
fi

# Install kubectl if not present
if ! command -v kubectl &> /dev/null; then
    echo "Please install kubectl for Kubernetes management"
fi

echo "Setup complete!"
