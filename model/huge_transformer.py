import numpy as np


def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    expx = np.exp(x)
    return expx / expx.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(q, k, v, mask=None):
    d = k.shape[-1]
    attn_logits = np.matmul(q, k.transpose(0, 1, 3, 2)) / np.sqrt(d)

    if mask is not None:
        attn_logits = np.where(mask[None, None, :, :], -1e10, attn_logits)

    attn_weights = softmax(attn_logits, axis=-1)
    out = np.matmul(attn_weights, v)
    return out, attn_weights


class HugeTransformer:
    def __init__(self, vocab_size, n_embd=256, n_head=8, n_layer=4, block_size=32):
        d = n_embd // n_head
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.n_head = n_head
        self.n_layer = n_layer
        self.d = d
        self.block_size = block_size

        np.random.seed(42)
        self.tok_emb = np.random.normal(0, 0.1, (vocab_size, n_embd))
        self.pos_emb = np.random.normal(0, 0.1, (block_size, n_embd))

        self.Wq = []
        self.Wk = []
        self.Wv = []
        self.Wo = []
        self.W1 = []
        self.b1 = []
        self.W2 = []
        self.b2 = []
        self.ln1_eps = 1e-5

        for _ in range(n_layer):
            self.Wq.append(np.random.normal(0, 0.1, (n_embd, n_embd)))
            self.Wk.append(np.random.normal(0, 0.1, (n_embd, n_embd)))
            self.Wv.append(np.random.normal(0, 0.1, (n_embd, n_embd)))
            self.Wo.append(np.random.normal(0, 0.1, (n_embd, n_embd)))

            self.W1.append(np.random.normal(0, 0.1, (n_embd, 4 * n_embd)))
            self.b1.append(np.zeros((4 * n_embd,)))
            self.W2.append(np.random.normal(0, 0.1, (4 * n_embd, n_embd)))
            self.b2.append(np.zeros((n_embd,)))

        self.lm_head = np.random.normal(0, 0.1, (n_embd, vocab_size))

    def layernorm(self, x):
        mean = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return (x - mean) / np.sqrt(var + self.ln1_eps)

    def mlp(self, x, idx_layer):
        h = np.matmul(x, self.W1[idx_layer]) + self.b1[idx_layer]
        h = np.maximum(h, 0)
        h = np.matmul(h, self.W2[idx_layer]) + self.b2[idx_layer]
        return h

    def self_attn(self, x, idx_layer, mask=None):
        B, T, D = x.shape
        H, d = self.n_head, self.d

        q = np.matmul(x, self.Wq[idx_layer])
        k = np.matmul(x, self.Wk[idx_layer])
        v = np.matmul(x, self.Wv[idx_layer])

        q = q.reshape(B, T, H, d).transpose(0, 2, 1, 3)
        k = k.reshape(B, T, H, d).transpose(0, 2, 1, 3)
        v = v.reshape(B, T, H, d).transpose(0, 2, 1, 3)

        out, _ = scaled_dot_product_attention(q, k, v, mask=mask)
        out = out.transpose(0, 2, 1, 3).reshape(B, T, D)
        out = np.matmul(out, self.Wo[idx_layer])
        return out

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.block_size

        tok_emb = self.tok_emb[idx]
        pos_emb = self.pos_emb[np.arange(T)]
        x = tok_emb + pos_emb[None, ...]

        attn_mask = np.triu(np.ones((T, T), dtype=bool), k=1)

        for i in range(self.n_layer):
            x = x + self.self_attn(x, i, mask=attn_mask)
            x = self.layernorm(x)
            x = x + self.mlp(x, i)
            x = self.layernorm(x)

        logits = np.matmul(x, self.lm_head)

        loss = None
        if targets is not None:
            logits_flat = logits.reshape(-1, self.vocab_size)
            targets_flat = targets.reshape(-1)
            logits_flat = logits_flat - logits_flat.max(axis=-1, keepdims=True)
            exp_logits = np.exp(logits_flat)
            probs = exp_logits / exp_logits.sum(axis=-1, keepdims=True)
            logprobs = np.log(probs + 1e-10)
            loss = -logprobs[np.arange(len(targets_flat)), targets_flat].mean()

        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self.forward(idx_cond)
            logits = logits[0, -1, :]
            probs = softmax(logits, axis=-1)
            probs = np.clip(probs, 1e-12, None)
            probs = probs / probs.sum()
            next_id = np.random.choice(len(probs), p=probs)
            idx = np.append(idx, [[next_id]], axis=1)

        return idx


def train_huge_model(bpe, vocab_size, text_corpus="hello world hello ai agent from scratch hello how are you fine thank you bye"):
    model = HugeTransformer(
        vocab_size=vocab_size,
        n_embd=256,
        n_head=8,
        n_layer=4,
        block_size=32,
    )

    tokens_list = bpe.encode(text_corpus)
    tokens = np.array(tokens_list).reshape(1, -1)

    print("\n=== HUGE 4-Layer NumPy Transformer Training ===")
    print("Model vocab size:", vocab_size)
    print("Token sequence length:", tokens.shape[1])

    L = tokens.shape[1]
    T = min(32, L - 1)
    if T < 2:
        raise ValueError("Corpus too short to train")

    for step in range(10000):
        start = np.random.randint(0, L - T)
        x = tokens[0, start:start + T].reshape(1, T)
        y = tokens[0, start + 1:start + T + 1].reshape(1, T)

        _, loss = model.forward(x, y)

        if step % 1000 == 0:
            print(f"Step {step:5d} | Loss: {loss:.4f}")

    print("\n=== Huge model generation (prefix: 'hello') ===")
    prefix = "hello"
    prefix_ids = bpe.encode(prefix)
    prefix_array = np.array(prefix_ids).reshape(1, -1)
    out = model.generate(prefix_array, max_new_tokens=60)
    raw = bpe.decode(out[0].tolist())
    print("Decoded text:", repr(raw))

    return model
