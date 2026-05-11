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
except (FileNotFoundError, pickle.UnpicklingError, OSError) as err:
    print(f"Model files could not be loaded: {err}", file=sys.stderr)
    sys.exit(1)

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
    print("Model loaded, but no usable prediction method was found.", file=sys.stderr)
    sys.exit(1)

if hasattr(output, "tolist"):
    output = output.tolist()

if isinstance(output, (list, tuple)) and len(output) == 1:
    output = output[0]

if hasattr(bpe, "decode") and not isinstance(output, str):
    reply = bpe.decode(output)
else:
    reply = output

print(str(reply).strip())
