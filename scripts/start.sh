#!/bin/bash
# Production Startup Script

set -e

echo "🚀 Starting Accounting AI Assistant..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

# Check if model is available
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "📥 Pulling llama3.2:3b model..."
    ollama pull llama3.2:3b
fi

# Initialize database
echo "📊 Initializing database..."
python scripts/init_db.py

# Start the application
echo "🎯 Starting FastAPI server..."
make run