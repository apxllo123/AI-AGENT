# model/huge_transformer.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class Head(nn.Module):
    def __init__(self, n_embd, head_size, block_size, dropout=0.1):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        v = self.value(x)
        
        wei = q @ k.transpose(-2, -1) * k.shape[-1]**-0.5
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        out = wei @ v
        return out

class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.1):
        super().__init__()
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([Head(n_embd, head_size, block_size, dropout) for _ in range(n_head)])
        self.proj = nn.Linear(head_size * n_head, n_embd)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out

class FeedFoward(nn.Module):
    def __init__(self, n_embd, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )
        
    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.1):
        super().__init__()
        self.sa = MultiHeadAttention(n_embd, n_head, block_size, dropout)
        self.ffwd = FeedFoward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)
        
    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

class TinyTransformer(nn.Module):
    def __init__(self, vocab_size, n_embd=384, block_size=256, n_head=6, n_layer=6, dropout=0.2):
        super().__init__()
        self.block_size = block_size
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        
    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        
        loss = None
        if targets is not None:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)
            
        return logits, loss
        
    def generate(self, idx, max_new_tokens=100, temperature=1.0, top_k=None):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
                
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

def train_tiny_model_pytorch(bpe, vocab_size, text_corpus, steps=5000, lr=3e-4, batch_size=64):
    """Proper training with PyTorch"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    model = TinyTransformer(vocab_size=vocab_size, n_embd=384, block_size=256, n_head=6, n_layer=6).to(device)
    
    tokens = bpe.encode(text_corpus)
    if len(tokens) < 1000:
        raise ValueError("Corpus too short! Need at least 1000 tokens.")
    
    data = torch.tensor(tokens, dtype=torch.long)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    print(f"\n=== Training Real Transformer ===")
    print(f"Parameters: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")
    print(f"Tokens: {len(tokens)}, Steps: {steps}")
    
    for step in range(steps):
        # Sample batch
        ix = torch.randint(len(tokens) - 257, (batch_size,))
        x = torch.stack([data[i:i+256] for i in ix]).to(device)
        y = torch.stack([data[i+1:i+257] for i in ix]).to(device)
        
        logits, loss = model(x, y)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        if step % 500 == 0 or step == steps - 1:
            print(f"Step {step:5d} | Loss: {loss.item():.4f}")
            
            # Test generation
            test_prompt = "hello"
            context = torch.tensor(bpe.encode(test_prompt), dtype=torch.long).unsqueeze(0).to(device)
            gen = model.generate(context, max_new_tokens=50, temperature=0.8)[0].tolist()
            print(f"  Sample: {bpe.decode(gen)[:100]}")
    
    return model

# Keep old function for compatibility but warn
def train_tiny_model_numpy(*args, **kwargs):
    print("⚠️ NumPy version is broken. Switching to PyTorch...")
    return train_tiny_model_pytorch(*args, **kwargs)
