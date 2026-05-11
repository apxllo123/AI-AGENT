import os
import pickle
import random
import sys

# Add current directory to path so we can import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

bpe = None
model = None

# Fallback responses
FALLBACK_RESPONSES = [
    "Hello! I'm your AI assistant. How can I help you today?",
    "That's interesting! Tell me more about that.",
    "I understand. What would you like to know more about?",
    "Thanks for sharing! I'm here to help.",
    "Great question! Let me think about that.",
    "I can help with many topics - just ask!",
    "That's a cool thought. Tell me more!",
    "I'm learning new things every day!",
    "What else would you like to discuss?",
    "I'm here to assist you with any questions.",
]

def get_fallback_reply(message):
    """Get a fallback reply based on keywords."""
    m = message.lower()
    if any(w in m for w in ["hello", "hi", "hey", "greetings"]):
        return "Hello there! How can I assist you today?"
    if any(w in m for w in ["help", "assist", "support"]):
        return "I'm here to help! What do you need assistance with?"
    if any(w in m for w in ["who are you", "name", "what are you"]):
        return "I'm AI-AGENT, an AI assistant built with a custom transformer model!"
    if any(w in m for w in ["what can you do", "abilities", "capabilities"]):
        return "I can chat, answer questions, help with tasks, and more! Just ask."
    if any(w in m for w in ["thanks", "thank you", "appreciate"]):
        return "You're welcome! Happy to help."
    if any(w in m for w in ["bye", "goodbye", "see you"]):
        return "Goodbye! Hope to chat again soon!"
    if any(w in m for w in ["weather", "time", "date"]):
        return "I'm not connected to live data, but I'd love to chat about any topic!"
    if any(w in m for w in ["weather", "news", "stock"]):
        return "I don't have real-time data access, but I can discuss many topics!"
    return random.choice(FALLBACK_RESPONSES)

# Try to load model with local code
try:
    from model.huge_transformer import TinyTransformer
    from tokenizer.transformer import SimpleBPE
    
    # Try loading artifacts
    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
    print(f"BPE loaded: {type(bpe)}")
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"Model loaded: {type(model)}")
    
except Exception as e:
    print(f"Model loading error: {e}")
    bpe = None
    model = None

@app.route("/")
def home():
    return jsonify({"status": "ok"})

@app.route("/reply", methods=["POST"])
def reply():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Try to use real model if loaded
    if bpe is not None and model is not None:
        try:
            # Encode input
            if hasattr(bpe, "encode"):
                encoded = bpe.encode(message)
                encoded = [encoded] if isinstance(encoded, int) else encoded
            else:
                encoded = [ord(c) % 100 for c in message[:16]]
            
            import numpy as np
            idx = np.array(encoded).reshape(1, -1)
            
            # Generate with model
            if hasattr(model, "generate"):
                output = model.generate(idx, max_new_tokens=30, temperature=0.8)
            elif hasattr(model, "forward"):
                logits, _ = model.forward(idx)
                output_idx = logits[0, -1].argmax()
                output = np.concatenate([idx, [[output_idx]], axis=1)
            
            # Decode output
            if hasattr(bpe, "decode"):
                try:
                    reply_text = bpe.decode(output[0].tolist())
                except:
                    reply_text = "".join(chr(c % 26 + 97) for c in output[0][:30])
            else:
                reply_text = "".join(chr(c % 26 + 97) for c in output[0])
            
            if reply_text and len(reply_text) > 2:
                return jsonify({"reply": reply_text.strip()})
        except Exception as e:
            print(f"Model error: {e}")
    
    # Fallback to keyword-based response
    return jsonify({"reply": get_fallback_reply(message)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
