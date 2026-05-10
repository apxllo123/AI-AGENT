import os
import sys
import pickle
from flask import Flask, request, jsonify
import numpy as np

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

app = Flask(__name__)

bpe = None
model = None
model_loaded = False


def load_model():
    global bpe, model, model_loaded

    if model_loaded:
        return

    bpe_path = os.path.join(repo_root, "artifacts", "bpe.pkl")
    model_path = os.path.join(repo_root, "artifacts", "model.pkl")

    if not os.path.exists(bpe_path):
        raise FileNotFoundError(f"Missing tokenizer file: {bpe_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing model file: {model_path}")

    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    model_loaded = True


@app.before_request
def ensure_model_loaded():
    if not model_loaded:
        load_model()


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "AI-AGENT is live"})


@app.route("/info", methods=["GET"])
def info():
    return jsonify(
        {
            "status": "running",
            "model": "huge 4-layer NumPy transformer",
            "bpe_vocab_size": len(bpe.vocab) if bpe else 0,
        }
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    max_new_tokens = data.get("max_new_tokens", 40)

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    token_ids = bpe.encode(prompt)
    x = np.array(token_ids).reshape(1, -1)

    out = model.generate(x, max_new_tokens)
    raw = bpe.decode(out[0].tolist())
    reply = raw.strip()

    return jsonify({"prompt": prompt, "reply": reply})


if __name__ == "__main__":
    load_model()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
