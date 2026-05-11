#!/bin/bash
# JARVIS ONE-CLICK SETUP
# Run this and you're done!

set -e

echo "🤖 JARVIS Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}📥 Installing Ollama...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
fi

# 2. Start Ollama
if ! pgrep -x "ollama" > /dev/null 2>&1; then
    echo -e "${YELLOW}🚀 Starting Ollama...${NC}"
    ollama serve &
    sleep 5
fi

# 3. Download model
echo -e "${YELLOW}📥 Checking AI model...${NC}"
ollama pull llama3 2>/dev/null || true

# 4. Start ngrok tunnel
echo -e "${YELLOW}🔗 Starting tunnel...${NC}"
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    brew install ngrok/ngrok/ngrok
fi

# Kill old ngrok
pkill -f "ngrok http" 2>/dev/null || true
sleep 1

# Start ngrok in background
ngrok http 11434 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 5

# Get the URL
TUNNEL_URL=$(curl -s localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo -e "${YELLOW}⚠️ Waiting for tunnel...${NC}"
    sleep 10
    TUNNEL_URL=$(curl -s localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*' | head -1)
fi

echo ""
echo -e "${GREEN}✅ JARVIS IS READY!${NC}"
echo ""
echo "Tunnel URL: $TUNNEL_URL"
echo ""
echo "To use with website:"
echo "1. Set this as Railway env var: OLLAMA_URL=$TUNNEL_URL"
echo "2. Or open http://localhost:11434 to chat locally"
echo ""
echo "Press Ctrl+C to stop"

# Keep running
wait $NGROK_PID
