"""Tiny GPT-style Transformer used by AI-AGENT.

This is an educational from-scratch model built with PyTorch. It is intentionally
small enough for free cloud notebooks, Codespaces, or a modest server. The agent
wrapper around it supplies tools/memory so the project feels useful even while
the tiny model is still learning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class TinyGPTConfig:
    vocab_size: int
    block_size: int = 128
    n_embd: int = 128
    n_head: int = 4
    n_layer: int = 4
    dropout: float = 0.15


class CausalSelfAttention(nn.Module):
    def __init__(self, config: TinyGPTConfig):
        super().__init__()
        if config.n_embd % config.n_head != 0:
            raise ValueError("n_embd must be divisible by n_head")
        self.n_head = config.n_head
        self.head_dim = config.n_embd // config.n_head
        self.key = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.query = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.value = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.proj = nn.Linear(config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)
        self.register_buffer(
            "tril", torch.tril(torch.ones(config.block_size, config.block_size))
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, time, channels = x.shape
        k = self.key(x).view(batch, time, self.n_head, self.head_dim).transpose(1, 2)
        q = self.query(x).view(batch, time, self.n_head, self.head_dim).transpose(1, 2)
        v = self.value(x).view(batch, time, self.n_head, self.head_dim).transpose(1, 2)

        weights = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        weights = weights.masked_fill(self.tril[:time, :time] == 0, float("-inf"))
        weights = F.softmax(weights, dim=-1)
        weights = self.dropout(weights)

        out = weights @ v
        out = out.transpose(1, 2).contiguous().view(batch, time, channels)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    def __init__(self, config: TinyGPTConfig):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, config: TinyGPTConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ff = FeedForward(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x


class GPTModel(nn.Module):
    def __init__(self, config: TinyGPTConfig):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.Sequential(*[TransformerBlock(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None):
        batch, time = idx.shape
        if time > self.config.block_size:
            raise ValueError(f"Sequence length {time} exceeds block_size {self.config.block_size}")

        token_emb = self.token_embedding(idx)
        pos = torch.arange(time, device=idx.device)
        pos_emb = self.position_embedding(pos)
        x = token_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int = 100,
        temperature: float = 0.8,
        top_k: Optional[int] = 40,
    ) -> torch.Tensor:
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config.block_size :]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-6)
            if top_k is not None:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits = logits.masked_fill(logits < values[:, [-1]], float("-inf"))
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


# Backwards-compatible alias for older imports.
TinyTransformer = GPTModel


def get_batch(data: torch.Tensor, block_size: int, batch_size: int, device: str):
    if len(data) <= block_size + 1:
        # Repeat tiny corpora so the model can still train in demo mode.
        repeats = (block_size + 2) // max(1, len(data)) + 1
        data = data.repeat(repeats)
    starts = torch.randint(0, len(data) - block_size - 1, (batch_size,))
    x = torch.stack([data[i : i + block_size] for i in starts]).to(device)
    y = torch.stack([data[i + 1 : i + block_size + 1] for i in starts]).to(device)
    return x, y


@torch.no_grad()
def estimate_loss(model: GPTModel, train_data, val_data, block_size, batch_size, device, eval_iters=20):
    model.eval()
    out: Dict[str, float] = {}
    for split, data in (("train", train_data), ("val", val_data)):
        losses = []
        for _ in range(eval_iters):
            xb, yb = get_batch(data, block_size, batch_size, device)
            _, loss = model(xb, yb)
            losses.append(loss.item())
        out[split] = sum(losses) / len(losses)
    model.train()
    return out


def train_tiny_model_pytorch(
    *,
    bpe,
    vocab_size: int,
    text_corpus: str,
    steps: int = 1500,
    lr: float = 3e-4,
    batch_size: int = 32,
    block_size: int = 128,
    n_embd: int = 128,
    n_head: int = 4,
    n_layer: int = 4,
    dropout: float = 0.15,
    device: Optional[str] = None,
    eval_interval: int = 150,
) -> GPTModel:
    """Train a tiny GPT model and return it."""
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    config = TinyGPTConfig(
        vocab_size=vocab_size,
        block_size=block_size,
        n_embd=n_embd,
        n_head=n_head,
        n_layer=n_layer,
        dropout=dropout,
    )
    model = GPTModel(config).to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Device: {device}")

    ids = bpe.encode(text_corpus, add_special_tokens=True)
    if len(ids) < 50:
        print("Warning: corpus is extremely small. Add more examples to data/*.txt.")
    data = torch.tensor(ids, dtype=torch.long)
    split = max(1, int(0.9 * len(data)))
    train_data = data[:split]
    val_data = data[split:] if split < len(data) - 1 else data

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    for step in range(steps + 1):
        if step % eval_interval == 0:
            losses = estimate_loss(
                model, train_data, val_data, block_size, batch_size, device, eval_iters=10
            )
            print(
                f"step {step:5d} | train loss {losses['train']:.3f} | val loss {losses['val']:.3f}"
            )

        xb, yb = get_batch(train_data, block_size, batch_size, device)
        _, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    return model


def checkpoint_from_model(model: GPTModel) -> dict:
    return {"model_state": model.state_dict(), "config": asdict(model.config)}


def model_from_checkpoint(checkpoint: dict, map_location="cpu") -> GPTModel:
    config_dict = checkpoint.get("config") or {
        "vocab_size": checkpoint["vocab_size"],
        "block_size": checkpoint.get("block_size", 128),
        "n_embd": checkpoint.get("n_embd", 128),
        "n_head": checkpoint.get("n_head", 4),
        "n_layer": checkpoint.get("n_layer", 4),
        "dropout": checkpoint.get("dropout", 0.15),
    }
    config = TinyGPTConfig(**config_dict)
    model = GPTModel(config)
    state = checkpoint.get("model_state") or checkpoint.get("model_state_dict") or checkpoint
    model.load_state_dict(state)
    model.to(map_location)
    model.eval()
    return model
