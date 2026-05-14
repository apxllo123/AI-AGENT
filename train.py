import os
import pickle
import random

# Import from our improved modules
from tokenizer.transformer import SimpleBPE
from model.huge_transformer import train_tiny_model_numpy

# ==================== CONFIG ====================
os.makedirs("artifacts", exist_ok=True)
os.makedirs("data", exist_ok=True)

DATA_PATH = "data/tiny_data.txt"
ARTIFACTS_DIR = "artifacts"

# ==================== LOAD / CREATE TRAINING DATA ====================
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        corpus = f.read().strip()
    print(f"✅ Loaded training data: {len(corpus)} characters")
else:
    # Create better default corpus focused on your goals
    print("⚠️ No data/tiny_data.txt found. Using enhanced default corpus.")
    corpus = """
hello world hello ai agent from scratch.
I want to build an AI that can fix code and make money.
How can I create a freelance coding agent?
Let's build a trading bot that makes profit.
Fix this python bug and explain it.
I need ideas to make money online with AI.
AI agent that learns from every conversation.
"""
    # Save it for next time
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(corpus.strip())

# ==================== TRAIN BPE TOKENIZER ====================
print("\n=== Training BPE Tokenizer ===")
bpe = SimpleBPE()
bpe.train(corpus, num_merges=50)   # Increased merges for better vocab
vocab_size = len(bpe.vocab)

print(f"Vocab size: {vocab_size}")
print("Sample vocab:", list(bpe.vocab.keys())[:20])

# ==================== TRAIN THE MODEL ====================
print("\n=== Starting Model Training ===")
model = train_tiny_model_numpy(
    bpe=bpe,
    vocab_size=vocab_size,
    text_corpus=corpus,
    steps=2500,           # You can increase this if it runs okay
    lr=8e-4               # Lower learning rate for stability
)

# ==================== SAVE ARTIFACTS ====================
with open(os.path.join(ARTIFACTS_DIR, "bpe.pkl"), "wb") as f:
    pickle.dump(bpe, f)

with open(os.path.join(ARTIFACTS_DIR, "model.pkl"), "wb") as f:
    pickle.dump(model, f)

print("\n🎉 Training completed and artifacts saved!")
print(f"   → {ARTIFACTS_DIR}/bpe.pkl")
print(f"   → {ARTIFACTS_DIR}/model.pkl")
print("\nYou can now run the Python service!")
