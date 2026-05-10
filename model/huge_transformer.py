import numpy as np


def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    expx = np.exp(x)
    return expx / expx.sum(axis=axis, keepdims=True)


class TinyTransformer:
    def __init__(self, vocab_size, n_embd=64, block_size=32, seed=42):
        np.random.seed(seed)
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.block_size = block_size

        self.tok_emb = np.random.normal(0, 0.02, (vocab_size, n_embd))
        self.pos_emb = np.random.normal(0, 0.02, (block_size, n_embd))
        self.W1 = np.random.normal(0, 0.02, (n_embd, n_embd))
        self.b1 = np.zeros((n_embd,))
        self.W2 = np.random.normal(0, 0.02, (n_embd, vocab_size))
        self.b2 = np.zeros((vocab_size,))

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.block_size

        x = self.tok_emb[idx] + self.pos_emb[np.arange(T)][None, :, :]
        h = np.tanh(np.matmul(x, self.W1) + self.b1)
        logits = np.matmul(h, self.W2) + self.b2

        loss = None
        if targets is not None:
            logits_flat = logits.reshape(-1, self.vocab_size)
            targets_flat = targets.reshape(-1)

            probs = softmax(logits_flat, axis=-1)
            probs = np.clip(probs, 1e-12, None)
            loss = -np.log(probs[np.arange(len(targets_flat)), targets_flat]).mean()

        return logits, loss

    def train_step(self, idx, targets, lr=1e-2):
        B, T = idx.shape
        x = self.tok_emb[idx] + self.pos_emb[np.arange(T)][None, :, :]
        h = np.tanh(np.matmul(x, self.W1) + self.b1)
        logits = np.matmul(h, self.W2) + self.b2

        logits_flat = logits.reshape(-1, self.vocab_size)
        targets_flat = targets.reshape(-1)

        probs = softmax(logits_flat, axis=-1)
        probs = np.clip(probs, 1e-12, None)

        loss = -np.log(probs[np.arange(len(targets_flat)), targets_flat]).mean()

        dlogits = probs
        dlogits[np.arange(len(targets_flat)), targets_flat] -= 1
        dlogits /= len(targets_flat)
        dlogits = dlogits.reshape(B, T, self.vocab_size)

        dW2 = np.matmul(h.reshape(-1, self.n_embd).T, dlogits.reshape(-1, self.vocab_size))
        db2 = dlogits.sum(axis=(0, 1))

        dh = np.matmul(dlogits, self.W2.T)
        dtanh = dh * (1 - h ** 2)

        dW1 = np.matmul(x.reshape(-1, self.n_embd).T, dtanh.reshape(-1, self.n_embd))
        db1 = dtanh.sum(axis=(0, 1))

        dx = np.matmul(dtanh, self.W1.T).reshape(B, T, self.n_embd)

        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1

        for b in range(B):
            for t in range(T):
                self.tok_emb[idx[b, t]] -= lr * dx[b, t]
        self.pos_emb[:T] -= lr * dx.sum(axis=0)

        return loss

    def generate(self, idx, max_new_tokens, temperature=1.0):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self.forward(idx_cond)
            logits = logits[0, -1, :] / max(temperature, 1e-8)
            probs = softmax(logits, axis=-1)
            next_id = np.random.choice(self.vocab_size, p=probs)
            idx = np.concatenate([idx, np.array([[next_id]])], axis=1)
        return idx


def train_tiny_model_numpy(bpe, vocab_size, text_corpus, steps=2000, lr=1e-2):
    model = TinyTransformer(vocab_size=vocab_size, n_embd=64, block_size=32)
    tokens = bpe.encode(text_corpus, add_special_tokens=True)

    if len(tokens) < 4:
        raise ValueError("Corpus too short to train")

    print("\n=== Tiny NumPy Transformer Training ===")
    print("Vocab size:", vocab_size)
    print("Token length:", len(tokens))

    for step in range(steps):
        start = np.random.randint(0, max(1, len(tokens) - 3))
        end = min(start + 16, len(tokens) - 1)
        x = np.array(tokens[start:end]).reshape(1, -1)
        y = np.array(tokens[start + 1:end + 1]).reshape(1, -1)

        loss = model.train_step(x, y, lr=lr)

        if step % 200 == 0:
            print(f"Step {step:5d} | Loss: {loss:.4f}")

    print("\n=== Generation test ===")
    prefix = bpe.encode("hello", add_special_tokens=True)
    out = model.generate(np.array(prefix).reshape(1, -1), max_new_tokens=20)
    print("Decoded:", repr(bpe.decode(out[0].tolist())))

    return model
