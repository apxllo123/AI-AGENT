import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    expx = np.exp(x)
    return expx / expx.sum(axis=axis, keepdims=True)


class TinyTransformer:
    def __init__(self, vocab_size, n_embd=96, block_size=64, n_layer=2, seed=42):
        np.random.seed(seed)
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.block_size = block_size
        self.n_layer = n_layer
        
        # Token + Position embeddings
        self.tok_emb = np.random.normal(0, 0.02, (vocab_size, n_embd))
        self.pos_emb = np.random.normal(0, 0.02, (block_size, n_embd))
        
        # Simple multi-layer feedforward
        self.layers = []
        for _ in range(n_layer):
            layer = {
                'W1': np.random.normal(0, 0.02, (n_embd, n_embd * 2)),
                'b1': np.zeros((n_embd * 2,)),
                'W2': np.random.normal(0, 0.02, (n_embd * 2, n_embd)),
                'b2': np.zeros((n_embd,)),
            }
            self.layers.append(layer)
        
        # Output head
        self.W_out = np.random.normal(0, 0.02, (n_embd, vocab_size))
        self.b_out = np.zeros((vocab_size,))

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.block_size
        
        x = self.tok_emb[idx] + self.pos_emb[:T]
        
        # Multi-layer processing
        for layer in self.layers:
            h = np.tanh(np.matmul(x, layer['W1']) + layer['b1'])
            x = np.tanh(np.matmul(h, layer['W2']) + layer['b2']) + x  # residual
        
        logits = np.matmul(x, self.W_out) + self.b_out
        
        loss = None
        if targets is not None:
            logits_flat = logits.reshape(-1, self.vocab_size)
            targets_flat = targets.reshape(-1)
            probs = softmax(logits_flat, axis=-1)
            probs = np.clip(probs, 1e-12, None)
            loss = -np.log(probs[np.arange(len(targets_flat)), targets_flat]).mean()
        
        return logits, loss

    def generate(self, idx, max_new_tokens=50, temperature=0.85, top_k=40):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self.forward(idx_cond)
            logits = logits[0, -1, :] / max(temperature, 1e-8)
            
            # Top-k sampling
            if top_k > 0:
                v, _ = np.topk(logits, min(top_k, self.vocab_size))
                logits[logits < v[-1]] = -float('inf')
            
            probs = softmax(logits, axis=-1)
            next_id = np.random.choice(self.vocab_size, p=probs)
            idx = np.concatenate([idx, np.array([[next_id]])], axis=1)
        return idx


# ==================== TRAINING FUNCTION ====================
def train_tiny_model_numpy(bpe, vocab_size, text_corpus, steps=3000, lr=1e-3):
    model = TinyTransformer(
        vocab_size=vocab_size, 
        n_embd=96,      # increased a bit
        block_size=64, 
        n_layer=2
    )
    
    tokens = bpe.encode(text_corpus)
    if len(tokens) < 20:
        raise ValueError("Corpus too short!")
    
    print("\n=== Training TinyTransformer ===")
    print(f"Vocab size: {vocab_size} | Tokens: {len(tokens)}")
    
    for step in range(steps):
        # Sample random chunk
        start = np.random.randint(0, max(1, len(tokens) - 65))
        chunk = tokens[start:start+65]
        x = np.array(chunk[:-1]).reshape(1, -1)
        y = np.array(chunk[1:]).reshape(1, -1)
        
        loss = model.train_step(x, y, lr=lr)
        
        if step % 300 == 0 or step == steps-1:
            print(f"Step {step:5d} | Loss: {loss:.4f}")
    
    # Quick test generation
    print("\n=== Generation Test ===")
    test_prompt = "hello how are you"
    prefix = bpe.encode(test_prompt)
    out = model.generate(np.array(prefix).reshape(1, -1), max_new_tokens=30)
    print("Output:", repr(bpe.decode(out[0].tolist())))
    
    return model


# Add save/load methods to the class (optional but very useful)
TinyTransformer.save = lambda self, path: np.savez(path, 
    tok_emb=self.tok_emb, pos_emb=self.pos_emb, W_out=self.W_out, b_out=self.b_out,
    **{f"layer_{i}_{k}": v for i, layer in enumerate(self.layers) for k, v in layer.items()})

# Note: Loading would need a separate function - we can add later if needed
