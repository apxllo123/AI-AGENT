#!/bin/bash
# JARVIS Auto-Install Script
# Run this to set up Jarvis locally

set -e

echo "🤖 Installing JARVIS..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 required. Install from python.org"
    exit 1
fi

# Install requests
echo "📦 Installing requests..."
pip3 install requests 2>/dev/null || pip install requests

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "⚠️ Install Ollama manually from ollama.ai"
    fi
fi

# Start Ollama in background (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "🚀 Starting Ollama..."
        brew services start ollama 2>/dev/null || ollama serve &
        sleep 3
    fi
fi

# Download models
echo "📥 Downloading AI models (this may take a few minutes)..."
ollama pull llama3 2>/dev/null || true
ollama pull qwen2.5-coder 2>/dev/null || true

echo ""
echo "✅ JARVIS is ready!"
echo ""
echo "To start JARVIS, run:"
echo "  cd local-jarvis"
echo "  python3 main.py"
echo ""
