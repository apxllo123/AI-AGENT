import os
import sys
import json
from flask import Flask, request, jsonify
import numpy as np

# Add repo root to PYTHONPATH
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from model.huge_transformer import HugeTransformer, train_huge_model as train_tiny_model_numpy
from tokenizer.transformer import SimpleBPE


# ============ Global model / tokenizer ============
bpe = None
model = None
model_loaded = False


def load_model():
    global bpe, model, model_loaded

    if model_loaded:
        return

    # Load training data
    if os.path.exists("data/tiny_data.txt"):
        with open("data/tiny_data.txt", "r", encoding="utf-8") as f:
            corpus = f.read()
    else:
        corpus = "hello world hello ai agent from scratch"

    # Build tokenizer
    bpe = SimpleBPE()
    bpe.train(corpus, num_merges=12)
    vocab_size = len(bpe.vocab)

    # Load huge model
    model = train_tiny_model_numpy(bpe, vocab_size, text_corpus=corpus)

    model_loaded = True


app = Flask(__name__)


@app.before_request
def ensure_model_loaded():
    if not model_loaded:
        load_model()


@app.route("/chat", methods=["POST"])
def chat():
    if not model_loaded:
        load_model()

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    max_new_tokens = data.get("max_new_tokens", 40)

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    # Encode prompt
    token_ids = bpe.encode(prompt)
    x = np.array(token_ids).reshape(1, -1)

    # Generate
    out = model.generate(x, max_new_tokens)
    raw = bpe.decode(out[0].tolist())
    reply = raw.strip()

    return jsonify({"prompt": prompt, "reply": reply})


@app.route("/info", methods=["GET"])
def info():
    return jsonify(
        {
            "status": "running",
            "model": "huge 4-layer NumPy transformer",
            "bpe_vocab_size": len(bpe.vocab) if bpe else 0,
        }
    )


if __name__ == "__main__":
    load_model()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
