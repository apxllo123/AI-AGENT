"""Flask server for AI-AGENT inference."""

import os
import sys
import pickle

import numpy as np
from flask import Flask, jsonify, request, send_from_directory

from model.huge_transformer import HugeTransformer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

APP = Flask(__name__)

SITE_DIR = os.path.join(REPO_ROOT, "my-site")
CSS_DIR = os.path.join(SITE_DIR, "css")

BPE = None
MODEL = None
MODEL_LOADED = False


def load_model():
    """Load tokenizer and model artifacts from disk."""
    global BPE, MODEL, MODEL_LOADED

    if MODEL_LOADED:
        return

    bpe_path = os.path.join(REPO_ROOT, "artifacts", "bpe.pkl")
    model_path = os.path.join(REPO_ROOT, "artifacts", "model.pkl")

    if not os.path.exists(bpe_path):
        raise FileNotFoundError(f"Missing tokenizer file: {bpe_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing model file: {model_path}")

    with open(bpe_path, "rb") as file_obj:
        BPE = pickle.load(file_obj)

    with open(model_path, "rb") as file_obj:
        MODEL = pickle.load(file_obj)

    MODEL_LOADED = True


@APP.before_request
def ensure_model_loaded():
    """Load the model before handling a request."""
    if not MODEL_LOADED:
        load_model()


@APP.route("/", methods=["GET"])
def home():
    """Serve the UI."""
    return send_from_directory(SITE_DIR, "index.html")


@APP.route("/<path:filename>", methods=["GET"])
def site_files(filename):
    """Serve top-level site files like /index.html if requested."""
    return send_from_directory(SITE_DIR, filename)


@APP.route("/css/<path:filename>", methods=["GET"])
def css_files(filename):
    """Serve CSS files from my-site/css."""
    return send_from_directory(CSS_DIR, filename)


@APP.route("/info", methods=["GET"])
def info():
    """Return basic service information."""
    return jsonify(
        {
            "status": "running",
            "model": "huge 4-layer NumPy transformer",
            "bpe_vocab_size": len(BPE.vocab) if BPE else 0,
        }
    )


@APP.route("/chat", methods=["POST"])
def chat():
    """Generate a reply from the model."""
    data = request.get_json(silent=True) or {}
    prompt_text = data.get("prompt", "").strip()
    max_new_tokens = data.get("max_new_tokens", 40)

    if not prompt_text:
        return jsonify({"error": "prompt is required"}), 400

    token_ids = BPE.encode(prompt_text)
    inputs = np.array(token_ids).reshape(1, -1)

    output = MODEL.generate(inputs, max_new_tokens)
    raw_text = BPE.decode(output[0].tolist())
    reply = raw_text.strip()

    return jsonify({"prompt": prompt_text, "reply": reply})


if __name__ == "__main__":
    load_model()
    port = int(os.environ.get("PORT", 8080))
    APP.run(host="0.0.0.0", port=port, debug=False)
