#!/bin/bash
# ONE-CLICK JARVIS START
# Just run: bash START.sh

echo "🤖 Starting JARVIS..."

# Start Ollama if not running
pgrep ollama > /dev/null || ollama serve &

sleep 3

# Install & start ngrok if needed
which ngrok || brew install ngrok/ngrok/ngrok

# Kill old tunnel
pkill -f "ngrok http 11434" 2>/dev/null

# Start fresh tunnel  
ngrok http 11434 --log=stdout >/tmp/ngrok.log 2>&1 &
sleep 8

# Get URL
URL=$(curl -s localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"[^"]*' | cut -d'"' -f4)

echo "✅ Ollama Tunnel: $URL"
echo ""
echo "🔗 Copy this URL and set it in Railway as OLLAMA_URL"
echo "   Or just chat locally at http://localhost:11434"
echo ""

# Show in browser
open http://localhost:11434 2>/dev/null || true
