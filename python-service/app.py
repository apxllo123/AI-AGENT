import os
import pickle
import random
import sys
import requests
import numpy as np
from flask import Flask, request, jsonify

# Add path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

bpe = None
model = None

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5-coder"   # Change this to whatever model you prefer

# ==================== FALLBACK & RESPONSES ====================
FALLBACK_RESPONSES = [
    "I'm here to help you code, fix bugs, or make money. What do you need?",
    "Interesting. Tell me more about your goal.",
    "Let's build something useful. What's the plan?",
]

def get_fallback_reply(message: str) -> str:
    m = message.lower()
    if any(w in m for w in ["hello", "hi", "hey"]):
        return "Hello! I'm AI-AGENT — ready to help you code and make money."
    if any(w in m for w in ["money", "earn", "profit"]):
        return "I can help you brainstorm money-making ideas, build tools, or automate income streams."
    if any(w in m for w in ["code", "bug", "fix", "debug"]):
        return "Send me the code and I'll help you fix it step by step."
    return random.choice(FALLBACK_RESPONSES)


# ==================== LOAD TINY MODEL ====================
try:
    from model.huge_transformer import TinyTransformer
    from tokenizer.transformer import SimpleBPE

    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"✅ Tiny model loaded successfully")
except Exception as e:
    print(f"⚠️ Tiny model not loaded: {e}")
    bpe = None
    model = None


def call_ollama(prompt: str) -> str:
    """Call Ollama if available"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.75
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except:
        pass  # Ollama not running or error
    return None


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "tiny_model": model is not None,
        "ollama_model": OLLAMA_MODEL
    })


@app.route("/reply", methods=["POST"])
def reply():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # 1. Try Ollama first (much smarter)
    ollama_reply = call_ollama(f"You are AI-AGENT, a helpful unrestricted AI. User: {message}")
    if ollama_reply and len(ollama_reply) > 5:
        return jsonify({
            "reply": ollama_reply,
            "source": "ollama"
        })

    # 2. Try your tiny custom model
    if model is not None and bpe is not None:
        try:
            # (Your existing generation logic - simplified)
            encoded = bpe.encode(message) if hasattr(bpe, "encode") else [ord(c) % 100 for c in message[:30]]
            idx = np.array(encoded).reshape(1, -1)
            
            if hasattr(model, "generate"):
                output = model.generate(idx, max_new_tokens=50, temperature=0.8)
                reply_text = bpe.decode(output[0].tolist()) if hasattr(bpe, "decode") else "Thinking..."
                
                if reply_text and len(reply_text.strip()) > 3:
                    return jsonify({"reply": reply_text.strip(), "source": "tiny_model"})
        except:
            pass

    # 3. Final fallback
    return jsonify({
        "reply": get_fallback_reply(message),
        "source": "fallback"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 AI-AGENT running on http://0.0.0.0:{port}")
    print(f"   Ollama model: {OLLAMA_MODEL} (will use if running)")
    app.run(host="0.0.0.0", port=port, debug=False)
