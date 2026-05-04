# Accounting AI Assistant - Production Grade

## 🚀 Features

- ✅ **100% Local** - No cloud, no API keys, complete privacy
- ✅ **Guardrails Security** - PII detection, prompt injection prevention, content filtering
- ✅ **Production Middleware** - Rate limiting, authentication, logging, CORS
- ✅ **Complete Audit Trail** - All queries logged with risk scores
- ✅ **RAG Pipeline** - Accurate document retrieval with local LLM
- ✅ **Lightweight** - Runs on 4GB RAM with Llama 3.2 3B

## 📋 Prerequisites

- Python 3.10+
- Ollama installed: `curl -fsSL https://ollama.com/install.sh | sh`
- 4GB RAM minimum, 8GB recommended

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
cd Accounting_AI_Assistant

# 2. Complete setup (installs dependencies, pulls models, initializes DB)
make setup

# 3. Run the server
make run

# Server runs at: http://localhost:8000
# API Docs: http://localhost:8000/docs