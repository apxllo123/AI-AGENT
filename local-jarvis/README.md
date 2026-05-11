# 🤖 JARVIS - Your Local AI Assistant

A real AI assistant like Iron Man's JARVIS, powered by Ollama.

## Why Local?

- **Private**: Your conversations stay on your computer
- **No API costs**: Free, unlimited use
- **Your model**: Use any Ollama model (llama3, qwen, mistral, etc.)
- **Control**: You own the AI

## Quick Setup

### 1. Install Ollama
```bash
# macOS/Linux
brew install ollama

# Or download from https://ollama.ai
```

### 2. Start Ollama
```bash
ollama serve
```

### 3. Download a model
```bash
ollama pull llama3     # Recommended - good for conversation
# or
ollama pull qwen2.5-coder  # If you want coding focus
# or
ollama pull mistral
```

### 4. Run JARVIS
```bash
python main.py
```

That's it! Now chat with your own AI.

## Usage

```
You: hello
JARVIS: Good to see you, sir. What can I help you with?

You: write me a lua fly script
JARVIS: Here's a Roblox fly script...

You: what is machine learning
JARVIS: Machine learning is a subset of AI that...
```

## Changing the Model

Edit `main.py` and change:
```python
MODEL = "llama3"  # Change to "qwen2.5-coder", "mistral", etc.
```

## Requirements

- Python 3.8+
- `requests` library: `pip install requests`
- Ollama running locally

## Tips

- **For coding**: Use `qwen2.5-coder` 
- **For conversation**: Use `llama3` or `mistral`
- **For speed**: Use smaller models like `phi3`

## Optional: Add Voice

Want voice input/output? Install:
```bash
pip install speechrecognition pyttsx3
```

Then add voice functions. Let me know if you want that added!
