#!/bin/bash
# Verification script to check pipeline artifacts in MinIO

set -e

MINIO_ENDPOINT="http://minio-service.kubeflow.svc.cluster.local:9000"
MINIO_ACCESS_KEY="minio"
MINIO_SECRET_KEY="minio123"

echo "=== Pipeline Artifacts Verification ==="
echo ""

# Configure AWS CLI for MinIO
export AWS_ACCESS_KEY_ID=$MINIO_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$MINIO_SECRET_KEY

echo "1. Checking Model Signature..."
aws --endpoint-url $MINIO_ENDPOINT s3 ls s3://mlpipeline/signatures/ || echo "⚠ No signatures found"
echo ""

echo "2. Checking Garak Security Reports..."
aws --endpoint-url $MINIO_ENDPOINT s3 ls s3://mlpipeline/reports/ || echo "⚠ No reports found"
echo ""

echo "3. Checking Guardrails Configuration..."
aws --endpoint-url $MINIO_ENDPOINT s3 ls s3://mlpipeline/guardrails/ || echo "⚠ No guardrails config found"
echo ""

echo "=== Verification Complete ==="
