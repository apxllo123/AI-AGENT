# server/server.py
import os
import sys
import json
from flask import Flask, request, jsonify
import numpy as np

# Add repo root to PYTHONPATH so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.huge_transformer import HugeTransformer, train_huge_model as train_tiny_model_numpy
from tokenizer.transformer import SimpleBPE


bpe = None
model = None


def load_model():
    global bpe, model

    if os.path.exists("data/tiny_data.txt"):
        with open("data/tiny_data.txt", "r", encoding="utf-8") as f:
            corpus = f.read()
    else:
        corpus = "hello world hello ai agent from scratch"

    bpe = SimpleBPE()
    bpe.train(corpus, num_merges=12)
    vocab_size = len(bpe.vocab)

    model = train_tiny_model_numpy(bpe, vocab_size, text_corpus=corpus)


app = Flask(__name__)


@app.before_first_request
def setup():
    load_model()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    max_new_tokens = data.get("max_new_tokens", 40)

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    input_ids = np.array(bpe.encode(prompt)).reshape(1, -1)
    out = model.generate(input_ids, max_new_tokens)
    raw = bpe.decode(out[0])
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
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
    )
