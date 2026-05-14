# train.py
import os
import pickle
import torch

from tokenizer.transformer import SimpleBPE
from model.huge_transformer import train_tiny_model_pytorch  # Use PyTorch version

os.makedirs("artifacts", exist_ok=True)
os.makedirs("data", exist_ok=True)

DATA_PATH = "data/tiny_data.txt"
ARTIFACTS_DIR = "artifacts"

# Load training data
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        corpus = f.read()
    print(f"✅ Loaded: {len(corpus)} chars")
else:
    print("⚠️ Create data/tiny_data.txt with lots of text!")
    exit(1)

# Train BPE
print("\n=== Training BPE ===")
bpe = SimpleBPE()
bpe.train(corpus, num_merges=200)  # Increased from 50
vocab_size = len(bpe.vocab)
print(f"Vocab size: {vocab_size}")

# Train model
print("\n=== Training Model ===")
model = train_tiny_model_pytorch(
    bpe=bpe,
    vocab_size=vocab_size,
    text_corpus=corpus,
    steps=10000,  # Increased steps
    lr=3e-4,
    batch_size=64
)

# Save properly
torch.save({
    'model_state': model.state_dict(),
    'vocab_size': vocab_size,
    'n_embd': 384,
    'block_size': 256,
    'n_head': 6,
    'n_layer': 6
}, os.path.join(ARTIFACTS_DIR, "model.pt"))

with open(os.path.join(ARTIFACTS_DIR, "bpe.pkl"), "wb") as f:
    pickle.dump(bpe, f)

print("\n✅ Training complete!")
print(f"Saved model.pt and bpe.pkl to {ARTIFACTS_DIR}/")
