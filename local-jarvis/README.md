# 🤖 JARVIS - Enhanced Local AI Assistant

A powerful local AI like Iron Man's JARVIS, powered by Ollama.

## Features

- **Auto Model Switch** - Uses qwen2.5-coder for code, llama3 for conversation
- **Web Search** - `search <query>` to search the web
- **File Operations** - `ls`, `cat` commands
- **Run Commands** - `run <command>` to execute shell commands
- **Open URLs** - `open <url>` to open in browser
- **Git** - `git <command>` directly
- **Status** - `status` shows system info

## Setup

```bash
# Install Ollama
brew install ollama

# Start Ollama
ollama serve

# Download models (optional but recommended)
ollama pull llama3
ollama pull qwen2.5-coder
ollama pull codellama
```

## Run

```bash
cd local-jarvis
pip install requests
python main.py
```

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search the web |
| `open <url>` | Open URL in browser |
| `run <cmd>` | Run shell command |
| `ls [path]` | List files |
| `cat <file>` | Show file |
| `git <cmd>` | Run git |
| `status` | System status |
| `help` | Show help |

## Usage

```
You: hello
JARVIS: Good to see you, sir. What can I help with?

You: write me a lua fly script
JARVIS: [Switching to qwen2.5-coder]
Here's a Roblox fly script...

You: search what is machine learning
JARVIS: Search results:
- Machine learning - Wikipedia
- Machine Learning | IBM
- What is Machine Learning? 

You: run ls
JARVIS: total 48
drwxr-xr-x  5 user  staff   160 May 11 04:17 .
drwxr-xr-xr-x  2 user  staff   160 May 11 04:18 local-jarvis
...

You: help
JARVIS: Special Commands:
  open <url>    - Open URL in browser
  run <cmd>     - Run shell command
  ls [path]      - List files
  cat <file>    - Show file contents
  search <query> - Web search
  git <cmd>     - Run git command
  status       - Show system status
  help          - Show this help
```

## Models

The AI auto-switches models based on what you're asking:

- **qwen2.5-coder** or **codellama** - For code/script requests
- **llama3** - For conversation and general questions
- **phi3** - Fast responses

## Requirements

- Python 3.8+
- `requests`: `pip install requests`
- Ollama running locally
