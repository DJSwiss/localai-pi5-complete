#!/bin/bash

echo "🚀 Starting COMPLETE Local AI Stack on Raspberry Pi 5..."
echo "===================================================="
echo "🤖 LocalAI + 🧠 LocalAGI + 🧠 LocalRecall + MCP"
echo "===================================================="

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo "📊 Available Memory: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 5000 ]; then
    echo "⚠️  Warning: Full stack requires significant memory (8GB Pi 5 recommended)."
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create all directories
echo "📁 Creating full stack directories..."
mkdir -p recall-state recall-assets chroma-data postgres-memory sql-init redis-sessions docprocessor

# Set permissions
chmod -R 777 recall-state recall-assets chroma-data postgres-memory redis-sessions docprocessor

echo "🚀 Starting Complete Local AI Stack..."
docker compose -f docker-compose.full-stack.yaml up -d

echo ""
echo "✅ Complete Local AI Stack is starting up..."
echo ""
echo "🌐 Available Services:"
echo "   • LocalAI Core: http://localhost:8080"
echo "   • LocalRecall (RAG): http://localhost:8088" 
echo "   • MCP + Recall: http://localhost:8093"
echo "   • Full Stack Agent: http://localhost:8090"
echo "   • ChromaDB: http://localhost:8000"
echo "   • Full Stack UI: http://localhost:8092"
echo "   • Document Processor: http://localhost:8089"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "🧠 Complete AI Capabilities:"
echo "   ✅ Chat & Text Generation (LocalAI)"
echo "   ✅ Autonomous Agents (LocalAGI)"
echo "   ✅ Long-term Memory (LocalRecall)"
echo "   ✅ Semantic Search & RAG"
echo "   ✅ Vector Database (ChromaDB)"
echo "   ✅ Document Processing (PDF, DOCX, Images)"
echo "   ✅ Persistent Memory (PostgreSQL)"
echo "   ✅ Session Management (Redis)"
echo "   ✅ Advanced MCP Tools"
echo "   ✅ System Monitoring & Management"
echo ""
echo "📚 Memory & Knowledge Features:"
echo "   • Upload documents → Automatic vectorization"
echo "   • Ask questions → RAG-enhanced answers"
echo "   • Conversations → Stored in long-term memory"
echo "   • Context → Persists across sessions"
echo "   • Search → Semantic similarity matching"
echo ""
echo "💬 Example Full Stack Interactions:"
echo "   • 'Remember that I prefer Python over JavaScript'"
echo "   • 'Upload my research papers and summarize the key findings'"
echo "   • 'What did we discuss about Docker optimization last week?'"
echo "   • 'Search my documents for information about Raspberry Pi performance'"
echo "   • 'Based on my uploaded data, what model would work best?'"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for full stack to be ready..."

# Wait for LocalAI Core
for i in {1..30}; do
    if curl -s http://localhost:8080/readyz > /dev/null 2>&1; then
        echo "✅ LocalAI Core is ready!"
        break
    fi
    echo "⏳ LocalAI Core starting... ($i/30)"
    sleep 5
done

# Wait for LocalRecall
for i in {1..20}; do
    if curl -s http://localhost:8088/ > /dev/null 2>&1; then
        echo "✅ LocalRecall is ready!"
        break
    fi
    echo "⏳ LocalRecall starting... ($i/20)"
    sleep 5
done

# Wait for ChromaDB
for i in {1..15}; do
    if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    echo "⏳ ChromaDB starting... ($i/15)"
    sleep 3
done

# Wait for Full Stack UI
for i in {1..20}; do
    if curl -s http://localhost:8092/ > /dev/null 2>&1; then
        echo "✅ Full Stack UI is ready!"
        break
    fi
    echo "⏳ Full Stack UI starting... ($i/20)"
    sleep 3
done

echo ""
echo "🎉 COMPLETE Local AI Stack is ready!"
echo ""
echo "🔗 Main Access Points:"
echo "   • Full Stack UI: http://localhost:8092"
echo "   • RAG Memory: http://localhost:8088"
echo "   • Vector DB: http://localhost:8000"
echo ""
echo "🧠 Your AI now has:"
echo "   • Permanent memory across all conversations"
echo "   • Ability to learn from uploaded documents"
echo "   • Semantic search through all knowledge"
echo "   • Context awareness spanning days/weeks/months"
echo "   • Document understanding (PDF, Word, images)"
echo ""
echo "🤖 The most advanced local AI setup possible on Pi 5! 🍓⚡🧠"