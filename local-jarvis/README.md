# 🤖 JARVIS - One-Click Setup

## Quick Start (just run this!)

```bash
cd local-jarvis
bash START.sh
```

That's it! It will:
1. Start Ollama (if not running)
2. Install ngrok (need tunnel to website)
3. Give you a URL to paste in Railway

## The Problem
Your website (Railway) can't connect to yourlocal Ollama because they're on different networks.

## The Fix
ngrok creates a tunnel from your computer to the web.

## After Starting
1. Copy the URL it shows (like `https://xxx.ngrok-free.app`)
2. Go to Railway → Your project → Variables
3. Add: `OLLAMA_URL` = that URL
4. Redeploy

Then your website will use your real AI!
