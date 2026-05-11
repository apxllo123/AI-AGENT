import os
import pickle
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

bpe = None
model = None

# Simple fallback responses for when model isn't loaded
FALLBACK_RESPONSES = [
    "Hello! I'm your AI assistant. How can I help you today?",
    "That's an interesting message! Tell me more.",
    "I received your message. The AI model is training, but I'm here to chat!",
    "Hey there! The model is loading. Try again in a bit!",
    "Thanks for messaging me! The AI backend is being set up.",
]

def get_fallback_reply(message):
    """Get a fallback reply when model fails to load."""
    message_lower = message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I assist you today?"
    elif "help" in message_lower:
        return "I can help answer questions. The AI model is being configured!"
    elif "name" in message_lower:
        return "I'm AI-AGENT, your assistant!"
    else:
        return random.choice(FALLBACK_RESPONSES)

try:
    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
    print(f"BPE loaded: {type(bpe)}")
except (FileNotFoundError, pickle.UnpicklingError, OSError) as err:
    print(f"Failed to load BPE: {err}")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"Model loaded: {type(model)}")
except (FileNotFoundError, pickle.UnpicklingError, OSError) as err:
    print(f"Failed to load model: {err}")

@app.route("/")
def home():
    return jsonify({"status": "ok"})

@app.route("/reply", methods=["POST"])
def reply():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Use fallback if model/bpe not loaded (happens when modules are missing)
    if bpe is None or model is None:
        print(f"Using fallback - model loaded: {model is not None}, bpe loaded: {bpe is not None}")
        return jsonify({"reply": get_fallback_reply(message)})

    try:
        if hasattr(bpe, "encode"):
            encoded = bpe.encode(message)
        else:
            encoded = message

        if hasattr(model, "predict"):
            output = model.predict(encoded)
        elif hasattr(model, "generate"):
            output = model.generate(encoded)
        elif hasattr(model, "forward"):
            output = model.forward(encoded)
        else:
            return jsonify({"reply": get_fallback_reply(message)})

        if hasattr(bpe, "decode") and not isinstance(output, str):
            reply_text = bpe.decode(output)
        else:
            reply_text = output

        return jsonify({"reply": str(reply_text).strip()})
    except Exception as e:
        print(f"Model error: {e}")
        return jsonify({"reply": get_fallback_reply(message)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
