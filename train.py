import os
import pickle

from tokenizer.transformer import SimpleBPE
from model.huge_transformer import train_tiny_model_numpy

os.makedirs("artifacts", exist_ok=True)

if os.path.exists("data/tiny_data.txt"):
    with open("data/tiny_data.txt", "r", encoding="utf-8") as f:
        corpus = f.read()
else:
    corpus = "hello world hello ai agent from scratch"

bpe = SimpleBPE()
bpe.train(corpus, num_merges=12)
vocab_size = len(bpe.vocab)

model = train_tiny_model_numpy(
    bpe=bpe,
    vocab_size=vocab_size,
    text_corpus=corpus,
    steps=2000,
    lr=1e-2,
)

with open("artifacts/bpe.pkl", "wb") as f:
    pickle.dump(bpe, f)

with open("artifacts/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("saved artifacts to artifacts/")
