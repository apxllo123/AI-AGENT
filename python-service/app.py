import os
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

base_dir = os.path.dirname(__file__)
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

try:
    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
except (FileNotFoundError, pickle.UnpicklingError, OSError) as err:
    bpe = None
    print(f"Failed to load BPE: {err}")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except (FileNotFoundError, pickle.UnpicklingError, OSError) as err:
    model = None
    print(f"Failed to load model: {err}")

@app.route("/reply", methods=["POST"])
def reply():
    if bpe is None or model is None:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

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
        return jsonify({"error": "No usable prediction method found"}), 500

    if hasattr(bpe, "decode") and not isinstance(output, str):
        reply_text = bpe.decode(output)
    else:
        reply_text = output

    return jsonify({"reply": str(reply_text).strip()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
