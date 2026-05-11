#!/usr/bin/env python3
"""
JARVIS - Local AI Assistant using Ollama
Run this on your computer to have a real AI brain
"""
import requests
import sys

# ==============================
# CONFIGURATION
# ==============================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"  # or "qwen2.5-coder", "mistral", etc.

SYSTEM_PROMPT = """You are Jarvis, a helpful AI assistant like Iron Man's JARVIS. 
You are concise, professional, a bit witty. You help with coding, explain tech, have conversations.
Keep responses natural, conversational, and not too long."""


def chat_with_jarvis(user_message, history=None):
    """Send message to Ollama and get response"""
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if history:
        messages.extend(history[-8:])  # Last 8 messages for context
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=120
        )
        
        if response.ok:
            return response.json()["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Is it running? Start: ollama serve"
    except requests.exceptions.Timeout:
        return "Timeout. The model is taking too long. Try a smaller model."
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    print("=" * 50)
    print("🤖 JARVIS - Local AI Assistant")
    print("=" * 50)
    print(f"Model: {MODEL}")
    print("Commands: quit/exit to close\n")
    
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
        
        print("JARVIS: ", end="", flush=True)
        response = chat_with_jarvis(user_input, history)
        print(response)
        
        # Save to history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
