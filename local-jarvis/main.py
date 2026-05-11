#!/usr/bin/env python3
"""
JARVIS - Enhanced Local AI Assistant
With auto model switching, file ops, web search, and more!
"""
import requests
import json
import subprocess
import os
import webbrowser
import urllib.request
from urllib.parse import quote_plus
from datetime import datetime

# ==============================
# CONFIGURATION
# ==============================
OLLAMA_URL = "http://localhost:11434/api/chat"

# Models for different tasks
MODELS = {
    "default": "llama3",
    "coding": "qwen2.5-coder", 
    "code": "codellama",
    "fast": "phi3",
}

CURRENT_MODEL = "llama3"

SYSTEM_PROMPT = """You are Jarvis, like Iron Man's AI. Professional, witty, concise.
You help with coding, explain tech, answer questions. Use code blocks when helpful."""


def search_web(query):
    """Search the web"""
    try:
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            # Extract titles
            titles = []
            import re
            for match in re.findall(r'<a class="result__a"[^>]*href="[^"]*"[^>]*>([^<]+)', html)[:5]:
                titles.append(match.strip())
            return titles[:3] if titles else ["No results"]
    except Exception as e:
        return [f"Error: {str(e)}"]


def detect_task(message):
    """Auto-detect what model to use"""
    m = message.lower()
    
    if any(w in m for w in ["code", "script", "write", "program", "function", "debug", "fix", "python", "lua", "javascript", "html", "css", "api"]):
        return "qwen2.5-coder"
    if any(w in m for w in ["search", "find", "look up", "google"]):
        return "llama3"  
    return "llama3"


def chat_with_jarvis(user_message, history=None, model=None):
    """Send message to Ollama"""
    if model is None:
        model = detect_task(user_message)
        if model != CURRENT_MODEL:
            print(f"[Switching to {model}] ", end="", flush=True)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if history:
        messages.extend(history[-8:])
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": messages, "stream": False},
            timeout=120
        )
        
        if response.ok:
            return response.json()["message"]["content"], model
        else:
            return f"Error: {response.status_code}", model
            
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Run: ollama serve", model
    except requests.exceptions.Timeout:
        return "Timeout. Try a smaller model.", model
    except Exception as e:
        return f"Error: {str(e)}", model


def run_command(cmd):
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, timeout=30
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {str(e)}"


def handle_special_commands(user_input):
    """Handle non-chat commands"""
    cmd = user_input.strip()
    
    # Open URLs
    if cmd.startswith("open "):
        url = cmd[5:].strip().strip('"')
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return "Opened in browser."
    
    # Run commands
    if cmd.startswith("run "):
        command = cmd[4:]
        return run_command(command)
    
    # File commands
    if cmd.startswith("ls"):
        path = cmd[3:].strip() or "."
        return run_command(f"ls -la {path}")
    
    if cmd.startswith("cat "):
        path = cmd[4:]
        try:
            with open(path, 'r') as f:
                return f.read()[:2000]
        except Exception as e:
            return f"Error: {e}"
    
    if cmd.startswith("search "):
        query = cmd[7:]
        results = search_web(query)
        return "Search results:\n" + "\n".join(f"- {r}" for r in results)
    
    # Git commands
    if cmd.startswith("git "):
        return run_command(cmd)
    
    # Check status
    if cmd == "status":
        return f"Model: {CURRENT_MODEL}\nOllama: Running\nTime: {datetime.now().strftime('%H:%M:%S')}"
    
    # Help
    if cmd == "help" or cmd == "commands":
        return """Special Commands:
  open <url>    - Open URL in browser
  run <cmd>     - Run shell command
  ls [path]     - List files
  cat <file>    - Show file contents
  search <query> - Web search
  git <cmd>     - Run git command
  status       - Show system status
  help         - Show this help"""
    
    return None


def main():
    print("=" * 50)
    print("🤖 JARVIS - Enhanced AI Assistant")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit\n")
    
    history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("JARVIS: Good bye, sir.")
            break
        
        # Check for special commands first
        special = handle_special_commands(user_input)
        if special:
            print("JARVIS:", special)
            continue
        
        # Normal chat with AI
        print("JARVIS: ", end="", flush=True)
        response, model = chat_with_jarvis(user_input, history)
        print(response)
        
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
