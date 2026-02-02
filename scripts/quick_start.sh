#!/bin/bash

# Quick start script for local development
echo "🚀 Starting LLM Security Pipeline (Local Development)"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run tests
echo "🧪 Running pipeline tests..."
python3 scripts/test_pipeline.py

echo "✅ Pipeline is ready!"
echo ""
echo "🔗 Service URLs:"
echo "  - Guardrails API: http://localhost:8000"
echo "  - Model Service: http://localhost:8080"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo "  - Jaeger: http://localhost:16686"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
