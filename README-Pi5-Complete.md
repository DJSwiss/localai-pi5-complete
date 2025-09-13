# 🍓🤖 LocalAI Complete Stack for Raspberry Pi 5

> **The Ultimate Local AI Setup**: LocalAI + LocalAGI + LocalRecall + MCP Integration optimized for Raspberry Pi 5

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)
[![Pi 5](https://img.shields.io/badge/Raspberry_Pi-5-red)](https://www.raspberrypi.org/products/raspberry-pi-5/)
[![LocalAI](https://img.shields.io/badge/LocalAI-Latest-green)](https://localai.io)

## 🚀 Features

### 🤖 **Complete Local AI Stack**
- **LocalAI**: OpenAI-compatible API server with no GPU requirements
- **LocalAGI**: Autonomous agents with function calling
- **LocalRecall**: RAG memory system with semantic search
- **MCP Integration**: Model Context Protocol for advanced tool usage

### 🎯 **Optimized for Raspberry Pi 5**
- ARM64 Docker containers
- Memory-efficient configurations (4GB/8GB variants)
- CPU-only inference with optimal threading
- Temperature monitoring and performance tuning

### 🧠 **Advanced Capabilities**
- 🗣️ **Voice Chat**: Speech-to-Text + Text-to-Speech
- 🎨 **Image Generation**: Stable Diffusion optimized for Pi 5
- 🔧 **System Tools**: Docker management, file operations, monitoring
- 📚 **Knowledge Base**: Document upload with automatic vectorization
- 🧠 **Long-term Memory**: Persistent conversation history
- 🔍 **Semantic Search**: RAG-powered question answering

## 🛠️ Quick Start

### Prerequisites
- Raspberry Pi 5 (4GB+ RAM recommended, 8GB ideal)
- Docker and Docker Compose installed
- 64GB+ SD card or SSD recommended

### 1. Clone Repository
```bash
git clone https://github.com/YOUR-USERNAME/localai-pi5-complete
cd localai-pi5-complete
```

### 2. Choose Your Setup Level

#### 🟢 **Basic LocalAI** (Lightweight)
```bash
./start-rpi5.sh
```
- **Services**: LocalAI API (8080), Web UI (8081)
- **Memory**: ~2GB
- **Features**: Chat, function calling, basic models

#### 🟡 **Training Environment**
```bash
./start-training.sh
```
- **Services**: + Jupyter Lab (8888), Ollama (11434), MLflow (5000)
- **Memory**: ~3-4GB
- **Features**: + Model fine-tuning, custom model creation

#### 🟠 **Agents System**
```bash
./start-agents.sh
```
- **Services**: + Agent orchestrator (8090), Tools (8091), Databases
- **Memory**: ~4-5GB
- **Features**: + Autonomous agents, advanced function calling

#### 🔵 **MCP Integration**
```bash
./start-mcp.sh
```
- **Services**: + MCP servers (8093-8097)
- **Memory**: ~5-6GB
- **Features**: + Advanced system integration, intelligent tool selection

#### 🔴 **Complete Stack** (Recommended)
```bash
./start-fullstack.sh
```
- **Services**: All + LocalRecall (8088), ChromaDB (8000), Document processor (8089)
- **Memory**: ~6-7GB (requires 8GB Pi 5)
- **Features**: Everything + RAG, persistent memory, document understanding

## 📊 Service Overview

| Service | Port | Description |
|---------|------|-------------|
| LocalAI API | 8080 | Main AI API server |
| LocalAI WebUI | 8081 | Web interface |
| LocalRecall | 8088 | RAG memory system |
| Agent Orchestrator | 8090 | Multi-agent system |
| Tools Server | 8091 | Function calling tools |
| Full Stack UI | 8092 | Complete dashboard |
| MCP Server | 8093 | Model Context Protocol |
| MCP Resources | 8094 | Data access layer |
| MCP Gateway | 8095 | Unified interface |
| Voice Agent | 8098 | Speech interface |
| ChromaDB | 8000 | Vector database |
| PostgreSQL | 5432 | Persistent storage |
| Redis | 6379 | Session management |

## 🎯 Usage Examples

### 💬 **Basic Chat**
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-2",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 🎨 **Image Generation**
```bash
curl -X POST http://localhost:8080/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute robot on Raspberry Pi 5",
    "size": "512x512"
  }'
```

### 🎤 **Voice Chat**
```bash
# Upload audio file for voice response
curl -X POST http://localhost:8098/voice-chat \
  -F "audio=@question.wav"
```

### 🧠 **Memory & RAG**
```python
import requests

# Store information in long-term memory
requests.post("http://localhost:8093/tools/memory_store", json={
    "content": "User prefers Python over JavaScript",
    "category": "preferences"
})

# Upload document to knowledge base
with open("document.pdf", "rb") as f:
    requests.post("http://localhost:8088/api/upload", 
                  files={"file": f}, 
                  data={"collection": "research"})

# Ask questions about uploaded documents
response = requests.post("http://localhost:8093/tools/smart_qa", json={
    "question": "What are the key findings in my research?",
    "search_knowledge": True
})
```

## 📁 Project Structure

```
localai-pi5-complete/
├── 🐳 Docker Compose Files
│   ├── docker-compose.rpi5.yaml      # Pi 5 optimized basic
│   ├── docker-compose.training.yaml  # Training environment
│   ├── docker-compose.agents.yaml    # Agents system
│   ├── docker-compose.mcp.yaml       # MCP integration
│   └── docker-compose.full-stack.yaml # Complete stack
├── 🚀 Startup Scripts
│   ├── start-rpi5.sh        # Basic setup
│   ├── start-training.sh    # Training environment
│   ├── start-agents.sh      # Agents system
│   ├── start-mcp.sh         # MCP integration
│   └── start-fullstack.sh   # Complete stack
├── ⚙️ Configuration
│   ├── .env.rpi5            # Pi 5 optimized settings
│   ├── .env.training        # Training configuration
│   └── CLAUDE.md            # Development guide
├── 🤖 Agents & MCP
│   ├── agents/              # Agent implementations
│   ├── mcp/                 # MCP servers & tools
│   ├── tools/               # Function calling tools
│   └── web-ui/              # Web interfaces
├── 📚 Data & Knowledge
│   ├── models/              # AI models storage
│   ├── training/            # Training data & notebooks
│   ├── recall-assets/       # Knowledge base documents
│   └── images/              # Generated images
└── 🧪 Testing & Examples
    ├── test-image-generation.py
    ├── test-audio-features.py
    └── notebooks/           # Jupyter tutorials
```

## 🎓 Key Features Explained

### 🧠 **Memory System (LocalRecall)**
- **Persistent Memory**: Conversations stored permanently
- **Document Upload**: PDF, DOCX, images automatically processed
- **Semantic Search**: Find information by meaning, not keywords
- **RAG Integration**: Answers enhanced with your documents

### 🤖 **Agent System**
- **4 Specialized Agents**: General, Research, Assistant, Code
- **Function Calling**: Agents can use tools automatically
- **MCP Protocol**: Advanced tool integration standard
- **System Integration**: Docker, file ops, monitoring built-in

### 🎨 **Multimedia Capabilities**
- **Text-to-Speech**: Natural voice responses
- **Speech-to-Text**: Voice input processing
- **Image Generation**: Stable Diffusion on Pi 5
- **Multi-language**: German, English, and more

### 📊 **Performance Optimization**
- **ARM64 Native**: Optimized for Pi 5 architecture
- **Memory Efficient**: Smart caching and model loading
- **CPU Threading**: Utilizes all 4 cores effectively
- **Temperature Aware**: Prevents throttling

## ⚡ Performance Benchmarks

### Raspberry Pi 5 (4GB/8GB)
| Task | Time | Memory Usage |
|------|------|-------------|
| Chat Response (phi-2) | 2-5 sec | ~1.5GB |
| Image Generation (512x512) | 2-5 min | ~2GB |
| Voice Processing (STT+TTS) | 3-8 sec | ~1GB |
| Document Upload & Indexing | 1-3 min | ~500MB |
| Semantic Search | <1 sec | ~100MB |

### Model Recommendations
- **phi-2** (2.7B): Default, balanced performance
- **gemma-2b** (2B): Faster, good quality
- **llama-3.2-1b** (1B): Fastest option
- **mistral-7b**: Higher quality (requires 8GB Pi 5)

## 🔧 Configuration

### Environment Variables

**Pi 5 Optimized Settings (.env.rpi5):**
```bash
THREADS=4              # Quad-core CPU
CONTEXT_SIZE=2048      # Memory/performance balance
F16=true              # Reduce memory usage
MMAP=true             # Efficient model loading
GPU_LAYERS=0          # CPU-only inference
TEMPERATURE_MONITOR=true
```

### Custom Models
1. Place `.gguf` files in `./models/`
2. Create YAML config in `./config/`
3. Update environment variables
4. Restart services

## 🚀 Advanced Usage

### Voice Conversations
```bash
# Start voice agent
python agents/voice_agent.py

# Record audio (Linux/Pi OS)
arecord -f cd -t wav question.wav

# Get voice response
curl -X POST http://localhost:8098/voice-chat \
  -F "audio=@question.wav"

# Play response
mpv ./audio/response_*.mp3
```

### Document Analysis
```bash
# Upload research papers
curl -X POST http://localhost:8088/api/upload \
  -F "file=@research.pdf" \
  -F "collection=papers"

# Ask complex questions
curl -X POST http://localhost:8093/tools/smart_qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize the methodology across all uploaded papers",
    "search_knowledge": true
  }'
```

### System Monitoring
```bash
# Get comprehensive system info
curl http://localhost:8093/tools/get_system_info?detailed=true

# Docker container management
curl -X POST http://localhost:8093/tools/manage_docker_containers \
  -d '{"action": "list"}'

# Network diagnostics
curl -X POST http://localhost:8093/tools/network_diagnostics \
  -d '{"target": "google.com", "test_type": "ping"}'
```

## 🛠️ Troubleshooting

### Common Issues

**Out of Memory:**
- Switch to smaller model (phi-2 → gemma-2b)
- Reduce CONTEXT_SIZE to 1024
- Add swap file: `sudo dphys-swapfile swapsize=2048`

**Slow Performance:**
- Check temperature: `cat /sys/class/thermal/thermal_zone0/temp`
- Ensure MMAP=true in configuration
- Consider SSD instead of SD card

**Service Not Starting:**
- Check logs: `docker compose -f docker-compose.full-stack.yaml logs [service]`
- Verify ports aren't in use: `netstat -tulpn | grep :8080`
- Ensure sufficient disk space: `df -h`

### Getting Help
- Check [CLAUDE.md](CLAUDE.md) for development guide
- View service logs for errors
- Monitor system resources during operation
- Test individual components before full stack

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/localai-pi5-complete
cd localai-pi5-complete

# Start basic setup for testing
./start-rpi5.sh

# Make changes and test
# Create pull request
```

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[LocalAI](https://github.com/mudler/LocalAI)** - Core AI server by Ettore Di Giacinto
- **[LocalRecall](https://github.com/mudler/LocalRecall)** - RAG memory system
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - By Anthropic
- **Raspberry Pi Foundation** - For amazing hardware
- **Open Source Community** - For model development and tools

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR-USERNAME/localai-pi5-complete&type=Date)](https://star-history.com/#YOUR-USERNAME/localai-pi5-complete&Date)

---

<div align="center">

**Made with ❤️ for the Raspberry Pi community**

*The most advanced local AI stack for Pi 5!* 🍓🤖

[⭐ Star this repo](https://github.com/YOUR-USERNAME/localai-pi5-complete) • [🍴 Fork it](https://github.com/YOUR-USERNAME/localai-pi5-complete/fork) • [📖 Documentation](CLAUDE.md)

</div>