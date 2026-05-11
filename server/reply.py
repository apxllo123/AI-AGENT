import os
import sys
import pickle

message = sys.argv[1] if len(sys.argv) > 1 else ""

base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "artifacts", "model.pkl")
bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)
except Exception:
    print("Model files could not be loaded.")
    sys.exit(0)

try:
    if hasattr(model, "generate_reply"):
        reply = model.generate_reply(message)
    elif hasattr(model, "predict"):
        reply = model.predict(message)
    else:
        reply = "Model loaded, but no reply method was found."
except Exception:
    reply = "Sorry, the model could not generate a reply right now."

print(str(reply))
