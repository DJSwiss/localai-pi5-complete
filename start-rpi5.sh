#!/bin/bash

echo "🍓 Starting LocalAI on Raspberry Pi 5..."
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo "📊 Available Memory: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 1500 ]; then
    echo "⚠️  Warning: Low memory detected. Consider closing other applications."
fi

# Create directories if they don't exist
mkdir -p models config images

# Check if Pi 5 config exists
if [ ! -f "docker-compose.rpi5.yaml" ]; then
    echo "❌ Pi 5 configuration not found. Using standard config..."
    docker compose up -d
else
    echo "🚀 Starting with Pi 5 optimizations..."
    docker compose -f docker-compose.rpi5.yaml --env-file .env.rpi5 up -d
fi

echo ""
echo "✅ LocalAI is starting up..."
echo "📱 API will be available at: http://localhost:8080"
echo "🌐 Web UI will be available at: http://localhost:8081"
echo ""
echo "📋 Useful commands:"
echo "   • View logs: docker compose -f docker-compose.rpi5.yaml logs -f"
echo "   • Stop: docker compose -f docker-compose.rpi5.yaml down"
echo "   • Check status: docker compose -f docker-compose.rpi5.yaml ps"
echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for API to be ready
for i in {1..30}; do
    if curl -s http://localhost:8080/readyz > /dev/null 2>&1; then
        echo "✅ LocalAI is ready!"
        echo "🔗 Try: curl http://localhost:8080/v1/models"
        break
    fi
    echo "⏳ Still starting... ($i/30)"
    sleep 5
done

echo "🎉 Setup complete! Happy AI-ing on your Pi 5! 🤖"