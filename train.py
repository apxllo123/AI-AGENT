#!/usr/bin/env python3
"""Train AI-AGENT's tiny from-scratch model.

Run locally, in GitHub Codespaces, Replit, or Google Colab from an iPad:

    pip install -r requirements.txt
    python train.py --quick

For better quality add more text to data/*.txt and increase --steps.
"""
from __future__ import annotations

import argparse
import os
import pickle
import shutil
from pathlib import Path

import torch

from model.huge_transformer import checkpoint_from_model, train_tiny_model_pytorch
from tokenizer.transformer import SimpleBPE


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
SERVICE_ARTIFACTS_DIR = ROOT / "python-service" / "artifacts"


def load_corpus(data_dir: Path, explicit_file: str | None = None) -> str:
    if explicit_file:
        paths = [Path(explicit_file)]
    else:
        paths = sorted(data_dir.glob("*.txt"))

    chunks = []
    for path in paths:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if text.strip():
                chunks.append(f"\n# source: {path.name}\n{text.strip()}\n")

    if not chunks:
        data_dir.mkdir(parents=True, exist_ok=True)
        starter = (
            "User: hello\nAssistant: Hello. I am your tiny from-scratch AI agent.\n\n"
            "User: what can you do\nAssistant: I can chat, remember notes, calculate, and help plan tasks.\n"
        )
        (data_dir / "tiny_data.txt").write_text(starter, encoding="utf-8")
        chunks.append(starter)

    corpus = "\n".join(chunks)
    # Encourage a chat format even when the user's data is plain text.
    if "Assistant:" not in corpus:
        corpus += (
            "\n\nUser: hello\nAssistant: Hello. How can I help?\n"
            "User: make a plan\nAssistant: Step 1: define the goal. Step 2: take one small action.\n"
        )
    return corpus


def parse_args():
    parser = argparse.ArgumentParser(description="Train the tiny AI-AGENT model")
    parser.add_argument("--data", help="Optional single training text file. Default: all data/*.txt")
    parser.add_argument("--out", default=str(ARTIFACTS_DIR), help="Artifact output directory")
    parser.add_argument("--steps", type=int, default=1500, help="Training steps")
    parser.add_argument("--quick", action="store_true", help="Fast smoke-test settings")
    parser.add_argument("--merges", type=int, default=200, help="Tokenizer merge count")
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--n-embd", type=int, default=128)
    parser.add_argument("--n-head", type=int, default=4)
    parser.add_argument("--n-layer", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--device", default=None, help="cpu, cuda, or leave blank for auto")
    parser.add_argument("--copy-to-service", action="store_true", default=True)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.quick:
        args.steps = min(args.steps, 200)
        args.block_size = min(args.block_size, 96)
        args.batch_size = min(args.batch_size, 16)
        args.n_embd = min(args.n_embd, 96)
        args.n_head = 4 if args.n_embd % 4 == 0 else 3
        args.n_layer = min(args.n_layer, 3)
        args.merges = min(args.merges, 80)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    corpus = load_corpus(DATA_DIR, args.data)
    print(f"Loaded corpus: {len(corpus):,} characters")

    print("\n=== Training tokenizer ===")
    bpe = SimpleBPE()
    bpe.train(corpus, num_merges=args.merges)

    print("\n=== Training tiny GPT model ===")
    model = train_tiny_model_pytorch(
        bpe=bpe,
        vocab_size=len(bpe.vocab),
        text_corpus=corpus,
        steps=args.steps,
        lr=args.lr,
        batch_size=args.batch_size,
        block_size=args.block_size,
        n_embd=args.n_embd,
        n_head=args.n_head,
        n_layer=args.n_layer,
        dropout=args.dropout,
        device=args.device,
    )

    model_path = out_dir / "model.pt"
    bpe_path = out_dir / "bpe.pkl"
    torch.save(checkpoint_from_model(model), model_path)
    with bpe_path.open("wb") as f:
        pickle.dump(bpe, f)

    print(f"\nSaved: {model_path}")
    print(f"Saved: {bpe_path}")

    if args.copy_to_service:
        SERVICE_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(model_path, SERVICE_ARTIFACTS_DIR / "model.pt")
        shutil.copy2(bpe_path, SERVICE_ARTIFACTS_DIR / "bpe.pkl")
        print(f"Copied artifacts to {SERVICE_ARTIFACTS_DIR}")

    prompt = "User: hello\nAssistant:"
    ids = torch.tensor([bpe.encode(prompt)], dtype=torch.long, device=next(model.parameters()).device)
    with torch.no_grad():
        generated = model.generate(ids, max_new_tokens=120, temperature=0.8, top_k=40)[0].tolist()
    print("\n=== Sample ===")
    print(bpe.decode(generated))


if __name__ == "__main__":
    main()
