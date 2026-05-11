import os
import sys
import pickle

base_dir = os.path.dirname(__file__)
message = sys.argv[1] if len(sys.argv) > 1 else ""

bpe_path = os.path.join(base_dir, "artifacts", "bpe.pkl")
model_path = os.path.join(base_dir, "artifacts", "model.pkl")

try:
    with open(bpe_path, "rb") as f:
        bpe = pickle.load(f)

    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception:
    print("Model files could not be loaded.")
    sys.exit(0)

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
        output = "Model loaded, but no usable prediction method was found."

    if hasattr(bpe, "decode") and not isinstance(output, str):
        reply = bpe.decode(output)
    else:
        reply = output
except Exception:
    reply = "Sorry, the model could not generate a reply right now."

print(str(reply).strip())
