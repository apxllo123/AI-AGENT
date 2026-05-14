import os
import pickle
import random
import sys
import numpy as np
from flask import Flask, request, jsonify

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

bpe = None
model = None

# ==================== FALLBACK RESPONSES ====================
FALLBACK_RESPONSES = [
    "Hello! I'm your AI-AGENT. How can I help you today?",
    "Interesting! Tell me more.",
    "I understand. What would you like to do next?",
    "I'm here to help with coding, ideas, or making money. Ask me anything!",
    "Good question! Let me think...",
    "That's a cool idea. Want me to expand on it?",
]

def get_fallback_reply(message: str) -> str:
    m = message.lower()
    if any(w in m for w in ["hello", "hi", "hey"]):
        return "Hello! I'm AI-AGENT, ready to help you code, make money, or learn."
    if any(w in m for w in ["who are you", "name"]):
        return "I'm AI-AGENT — a custom-built AI that can fix code, generate ideas, and help you earn."
    if any(w in m for w in ["what can you do", "abilities"]):
        return "I can help fix code, brainstorm money-making ideas, learn from conversations, and more!"
    if any(w in m for w in ["thank", "thanks"]):
        return "You're welcome! Let's keep building."
    return random.choice(FALLBACK_RESPONSES)


# ==================== LOAD MODEL ====================
try:
    from model.huge_transformer import TinyTransformer
    from tokenizer.transformer import SimpleBPE

    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
    print(f"✅ BPE tokenizer loaded: {type(bpe)}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"✅ Model loaded: {type(model)}")

except Exception as e:
    print(f"⚠️ Model loading failed: {e}")
    print("Falling back to keyword responses only.")
    bpe = None
    model = None


@app.route("/")
def home():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/reply", methods=["POST"])
def reply():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Try custom model first
    if model is not None and bpe is not None:
        try:
            # Encode
            if hasattr(bpe, "encode"):
                encoded = bpe.encode(message)
                if isinstance(encoded, int):
                    encoded = [encoded]
            else:
                # Very basic fallback encoding
                encoded = [ord(c) % bpe.vocab_size if hasattr(bpe, 'vocab_size') else 100 for c in message[:50]]

            idx = np.array(encoded, dtype=np.int32).reshape(1, -1)

            # Generate
            if hasattr(model, "generate"):
                output = model.generate(
                    idx, 
                    max_new_tokens=60, 
                    temperature=0.85,
                    top_k=40
                )
            else:
                # Simple forward pass fallback
                logits, _ = model.forward(idx)
                next_token = logits[0, -1].argmax()
                output = np.concatenate([idx, [[next_token]]], axis=1)

            # Decode
            if hasattr(bpe, "decode"):
                reply_text = bpe.decode(output[0].tolist())
            else:
                reply_text = "".join(chr((t % 26) + 97) for t in output[0][-30:])

            if reply_text and len(reply_text.strip()) > 3:
                return jsonify({"reply": reply_text.strip(), "source": "custom_model"})

        except Exception as e:
            print(f"Model generation error: {e}")

    # Fallback
    fallback = get_fallback_reply(message)
    return jsonify({"reply": fallback, "source": "fallback"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 AI-AGENT Python service starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
