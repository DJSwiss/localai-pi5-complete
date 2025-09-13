#!/bin/bash

echo "🧠 Starting LocalAI with MCP Integration on Raspberry Pi 5..."
echo "==========================================================="

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo "📊 Available Memory: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 4000 ]; then
    echo "⚠️  Warning: MCP requires significant memory. Consider 8GB Pi 5 variant."
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create MCP directories
echo "📁 Creating MCP directories..."
mkdir -p mcp mcp-redis mcp-postgres

# Set permissions
chmod -R 777 mcp

echo "🚀 Starting LocalAI with MCP Services..."
docker compose -f docker-compose.mcp.yaml up -d

echo ""
echo "✅ LocalAI + MCP Environment is starting up..."
echo ""
echo "🌐 Available Services:"
echo "   • LocalAI API: http://localhost:8080"
echo "   • MCP Server: http://localhost:8093"
echo "   • MCP Resources: http://localhost:8094" 
echo "   • MCP Gateway: http://localhost:8095"
echo "   • Enhanced Agent: http://localhost:8096"
echo "   • MCP Dashboard: http://localhost:8097"
echo ""
echo "🧠 MCP Capabilities:"
echo "   ✅ Advanced System Monitoring (CPU, Memory, Temperature)"
echo "   ✅ Docker Container Management (Start/Stop/Logs)"
echo "   ✅ Intelligent File Operations with Safety"
echo "   ✅ Network Diagnostics (Ping/Traceroute/Port Scan)"
echo "   ✅ AI Model Management and Metadata"
echo "   ✅ Dataset Access with Smart Caching"
echo "   ✅ Real-time Resource Monitoring"
echo "   ✅ Contextual Memory and Conversation History"
echo ""
echo "🔧 Enhanced Tools vs Basic LocalAI:"
echo "   • Basic LocalAI: Simple function calling"
echo "   • MCP Enhanced: Intelligent tool selection + context"
echo "   • Basic LocalAI: No persistent memory"
echo "   • MCP Enhanced: PostgreSQL + Redis for memory"
echo "   • Basic LocalAI: Manual resource access"
echo "   • MCP Enhanced: Automatic dataset/model discovery"
echo ""
echo "💬 Example MCP Interactions:"
echo "   • 'Show me system performance and suggest optimizations'"
echo "   • 'Analyze my datasets and recommend the best model'"
echo "   • 'Monitor Docker containers and restart failed ones'"
echo "   • 'Find all CSV files and show me their structure'"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for MCP services to be ready..."

# Wait for LocalAI
for i in {1..30}; do
    if curl -s http://localhost:8080/readyz > /dev/null 2>&1; then
        echo "✅ LocalAI is ready!"
        break
    fi
    echo "⏳ LocalAI starting... ($i/30)"
    sleep 5
done

# Wait for MCP Gateway
for i in {1..20}; do
    if curl -s http://localhost:8095/health > /dev/null 2>&1; then
        echo "✅ MCP Gateway is ready!"
        break
    fi
    echo "⏳ MCP Gateway starting... ($i/20)"
    sleep 3
done

# Wait for MCP Dashboard
for i in {1..20}; do
    if curl -s http://localhost:8097/ > /dev/null 2>&1; then
        echo "✅ MCP Dashboard is ready!"
        break
    fi
    echo "⏳ MCP Dashboard starting... ($i/20)"
    sleep 3
done

echo ""
echo "🎉 LocalAI + MCP is ready!"
echo ""
echo "🔗 Quick Access:"
echo "   • MCP Dashboard: http://localhost:8097"
echo "   • API Gateway: http://localhost:8095/docs"
echo "   • Health Check: http://localhost:8095/health"
echo ""
echo "🤖 Your AI is now MUCH more powerful with MCP! 🍓⚡"