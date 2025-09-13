#!/bin/bash

echo "🤖 Starting LocalAI Agents Environment on Raspberry Pi 5..."
echo "========================================================"

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo "📊 Available Memory: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 3000 ]; then
    echo "⚠️  Warning: Agents require significant memory. Consider closing other applications."
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create all necessary directories
echo "📁 Creating agent directories..."
mkdir -p agents tools web-ui agent-logs redis-data postgres-data

# Set permissions
chmod -R 777 agents tools web-ui agent-logs

echo "🚀 Starting LocalAI Agents Services..."
docker compose -f docker-compose.agents.yaml up -d

echo ""
echo "✅ LocalAI Agents Environment is starting up..."
echo ""
echo "🌐 Available Services:"
echo "   • LocalAI API: http://localhost:8080"
echo "   • Agent Orchestrator: http://localhost:8090"
echo "   • Tools Server: http://localhost:8091"
echo "   • Agent Web UI: http://localhost:8092"
echo "   • Redis (State): http://localhost:6379"
echo "   • PostgreSQL (Memory): http://localhost:5432"
echo ""
echo "🤖 Available Agent Types:"
echo "   ✅ General Purpose Agent - Multi-tool access"
echo "   ✅ Research Agent - Web search specialist"
echo "   ✅ Personal Assistant - Daily tasks & calculations"
echo "   ✅ Code Agent - Programming & development"
echo ""
echo "🛠️ Available Tools:"
echo "   ✅ Weather information"
echo "   ✅ Web search (DuckDuckGo)"
echo "   ✅ Mathematical calculations"
echo "   ✅ File operations"
echo "   ✅ System monitoring"
echo "   ✅ Network testing"
echo ""
echo "📋 Quick Start Commands:"
echo "   • Test API: curl http://localhost:8080/v1/models"
echo "   • List agents: curl http://localhost:8090/agents"
echo "   • View logs: docker compose -f docker-compose.agents.yaml logs -f"
echo "   • Stop all: docker compose -f docker-compose.agents.yaml down"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for LocalAI
for i in {1..30}; do
    if curl -s http://localhost:8080/readyz > /dev/null 2>&1; then
        echo "✅ LocalAI is ready!"
        break
    fi
    echo "⏳ LocalAI starting... ($i/30)"
    sleep 5
done

# Wait for Agent Orchestrator
for i in {1..20}; do
    if curl -s http://localhost:8090/ > /dev/null 2>&1; then
        echo "✅ Agent Orchestrator is ready!"
        break
    fi
    echo "⏳ Agent Orchestrator starting... ($i/20)"
    sleep 3
done

# Wait for Web UI
for i in {1..20}; do
    if curl -s http://localhost:8092/ > /dev/null 2>&1; then
        echo "✅ Agent Web UI is ready!"
        break
    fi
    echo "⏳ Agent Web UI starting... ($i/20)"
    sleep 3
done

echo ""
echo "🎉 LocalAI Agents Environment is ready!"
echo ""
echo "🔗 Quick Access Links:"
echo "   • Agent Chat UI: http://localhost:8092"
echo "   • API Documentation: http://localhost:8090/docs"
echo "   • Tools Documentation: http://localhost:8091/docs"
echo ""
echo "💬 Example Agent Interactions:"
echo "   • 'What's the weather like in London?'"
echo "   • 'Search for Raspberry Pi 5 benchmarks'"
echo "   • 'Calculate the factorial of 10'"
echo "   • 'Show me system information'"
echo ""
echo "🤖 Happy agent chatting on your Pi 5! 🍓"