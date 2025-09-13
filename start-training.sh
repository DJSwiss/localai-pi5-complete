#!/bin/bash

echo "🧠 Starting AI Model Training Environment on Raspberry Pi 5..."
echo "============================================================="

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo "📊 Available Memory: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 2000 ]; then
    echo "⚠️  Warning: Low memory for training. Consider closing other applications."
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create all necessary directories
echo "📁 Creating training directories..."
mkdir -p training/datasets training/models training/checkpoints notebooks ollama mlflow hf-cache

# Set permissions for Jupyter
chmod -R 777 training notebooks

echo "🚀 Starting AI Training Services..."
docker compose -f docker-compose.training.yaml --env-file .env.training up -d

echo ""
echo "✅ AI Training Environment is starting up..."
echo ""
echo "🌐 Available Services:"
echo "   • LocalAI API: http://localhost:8080"
echo "   • LocalAI Web UI: http://localhost:8081"
echo "   • Jupyter Lab: http://localhost:8888 (token: localai123)"
echo "   • Ollama: http://localhost:11434"
echo "   • MLflow: http://localhost:5000"
echo ""
echo "📚 Training Capabilities:"
echo "   ✅ Fine-tune existing models"
echo "   ✅ Create custom Ollama models"
echo "   ✅ Convert HuggingFace models to GGUF"
echo "   ✅ Experiment tracking with MLflow"
echo "   ✅ Interactive development with Jupyter"
echo ""
echo "📋 Quick Start Commands:"
echo "   • List models: curl http://localhost:8080/v1/models"
echo "   • Ollama create: docker exec ollama-server ollama create mymodel"
echo "   • View logs: docker compose -f docker-compose.training.yaml logs -f"
echo "   • Stop: docker compose -f docker-compose.training.yaml down"
echo ""

# Wait for Jupyter to be ready
echo "⏳ Waiting for Jupyter Lab to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:8888 > /dev/null 2>&1; then
        echo "✅ Jupyter Lab is ready!"
        echo "🔗 Open: http://localhost:8888 (token: localai123)"
        break
    fi
    echo "⏳ Jupyter starting... ($i/20)"
    sleep 5
done

echo ""
echo "🎉 AI Training Environment is ready!"
echo "📖 Check the tutorial notebook: notebooks/01_model_creation_tutorial.ipynb"
echo "🤖 Happy model training on your Pi 5! 🍓"