# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LocalAI setup optimized for Raspberry Pi 5 ARM64 architecture. LocalAI is a free, open-source alternative to OpenAI/Claude that runs locally with no GPU requirements.

## Quick Start Commands

### Raspberry Pi 5 Optimized Setup
```bash
# Basic LocalAI (lightweight)
./start-rpi5.sh

# Full training environment
./start-training.sh

# Agents with function calling
./start-agents.sh

# LocalAI + MCP integration
./start-mcp.sh

# COMPLETE STACK: LocalAI + LocalAGI + LocalRecall + MCP
./start-fullstack.sh
```

### Manual Docker Commands
```bash
# Pi 5 optimized LocalAI only
docker compose -f docker-compose.rpi5.yaml --env-file .env.rpi5 up -d

# With training capabilities  
docker compose -f docker-compose.training.yaml --env-file .env.training up -d

# Full agent environment
docker compose -f docker-compose.agents.yaml up -d

# Standard setup
docker compose up -d
```

## Available Services

### Basic Setup
- **LocalAI API**: http://localhost:8080
- **Web UI**: http://localhost:8081
- **Health Check**: http://localhost:8080/readyz

### Training Environment  
- **Jupyter Lab**: http://localhost:8888 (token: localai123)
- **Ollama**: http://localhost:11434
- **MLflow**: http://localhost:5000

### Agents Environment
- **Agent Web UI**: http://localhost:8092
- **Agent Orchestrator**: http://localhost:8090
- **Tools Server**: http://localhost:8091
- **Redis**: http://localhost:6379
- **PostgreSQL**: http://localhost:5432

### MCP Environment
- **MCP Server**: http://localhost:8093
- **MCP Resources**: http://localhost:8094
- **MCP Gateway**: http://localhost:8095
- **MCP Dashboard**: http://localhost:8097

### Complete Stack (LocalAI + LocalAGI + LocalRecall)
- **LocalAI Core**: http://localhost:8080
- **LocalRecall (RAG)**: http://localhost:8088
- **ChromaDB (Vector)**: http://localhost:8000
- **Full Stack UI**: http://localhost:8092
- **Document Processor**: http://localhost:8089
- **Memory (PostgreSQL)**: localhost:5432
- **Sessions (Redis)**: localhost:6379

## Raspberry Pi 5 Optimizations

### Performance Settings
- **Threads**: 4 (matches Pi 5's CPU cores)
- **Context Size**: 2048 (balanced for memory)
- **Memory Limit**: 6GB (adjust based on 4GB/8GB Pi 5 variant)
- **MMAP**: Enabled for efficient memory usage

### Recommended Models for Pi 5
- **phi-2** (2.7B) - Default, good balance
- **gemma-2b** (2B) - Lightweight, faster
- **llama-3.2-1b** (1B) - Fastest option
- **phi-3-mini** (3.8B) - Higher quality, slower

### Features Enabled on Pi 5
- ✅ Text Generation
- ✅ Text-to-Speech (TTS)
- ✅ Speech-to-Text (STT)
- ✅ Model Gallery Access
- ⚠️ Image Generation (disabled by default, resource intensive)

## File Structure

```
├── docker-compose.rpi5.yaml    # Pi 5 optimized configuration
├── .env.rpi5                   # Pi 5 environment variables
├── docker-compose.yaml         # Standard configuration
├── models/                     # Downloaded models storage
├── config/                     # Configuration files
└── images/                     # Generated images storage
```

## AI Model Creation & Training

### Training Environment
```bash
# Start full training environment
./start-training.sh

# Or manually:
docker compose -f docker-compose.training.yaml --env-file .env.training up -d
```

### Available Training Services
- **Jupyter Lab**: http://localhost:8888 (token: localai123)
- **Ollama**: http://localhost:11434 (model management)
- **MLflow**: http://localhost:5000 (experiment tracking)
- **HuggingFace Hub**: Integrated model access

### Model Creation Methods
1. **Fine-tuning**: Adapt existing small models (117M-3B parameters)
2. **Ollama Models**: Create custom models with system prompts
3. **GGUF Conversion**: Convert HuggingFace models to LocalAI format
4. **From Scratch**: Limited training of very small models

### Pi 5 Training Limitations
- **Memory**: Max ~6GB available for training
- **CPU Only**: No GPU acceleration
- **Recommended**: Fine-tuning models <3B parameters
- **Batch Size**: 1-2 (use gradient accumulation)

### Training Workflow
1. Open Jupyter Lab: `http://localhost:8888`
2. Follow tutorial: `notebooks/01_model_creation_tutorial.ipynb`
3. Convert to GGUF format for LocalAI
4. Deploy via LocalAI API

## Development Notes

- LocalAI automatically downloads required models on first request
- All processing happens locally - no data leaves your Pi
- API is OpenAI-compatible for easy integration
- Web UI available for easy model management and testing
- Resource usage monitored via Docker health checks
- Training data stored in `./training/datasets/`
- Models output to `./training/models/`

## Common Troubleshooting

- **Out of Memory**: Reduce CONTEXT_SIZE or switch to smaller model
- **Slow Performance**: Ensure MMAP is enabled, consider phi-2 or smaller models
- **Models Not Loading**: Check ./models directory permissions and disk space
- **Training Issues**: Use batch_size=1, enable gradient_accumulation_steps
- **Jupyter Not Accessible**: Check if port 8888 is available and container is running