# model/transformer_pytorch.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

class Head(nn.Module):
    """Single attention head"""
    def __init__(self, head_size, block_size, dropout=0.2):
        super().__init__()
        self.key = nn.Linear(head_size, head_size, bias=False)
        self.query = nn.Linear(head_size, head_size, bias=False)
        self.value = nn.Linear(head_size, head_size, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)      # (B, T, C)
        q = self.query(x)    # (B, T, C)
        v = self.value(x)    # (B, T, C)
        
        # Scaled dot-product attention
        wei = (q @ k.transpose(-2, -1)) * (C ** -0.5)  # Scale BEFORE softmax
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        
        out = wei @ v
        return out


class MultiHeadAttention(nn.Module):
    """Multi-head attention"""
    def __init__(self, n_emb, n_head, block_size, dropout=0.2):
        super().__init__()
        assert n_emb % n_head == 0
        self.heads = nn.ModuleList([
            Head(n_emb // n_head, block_size, dropout) 
            for _ in range(n_head)
        ])
        self.proj = nn.Linear(n_emb, n_emb)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    """Position-wise feed-forward network"""
    def __init__(self, n_emb, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_emb, 4 * n_emb),
            nn.GELU(),
            nn.Linear(4 * n_emb, n_emb),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    """Transformer encoder block with self-attention and feed-forward"""
    def __init__(self, n_emb, n_head, block_size, dropout=0.2):
        super().__init__()
        self.sa = MultiHeadAttention(n_emb, n_head, block_size, dropout)
        self.ffwd = FeedForward(n_emb, dropout)
        self.ln1 = nn.LayerNorm(n_emb)
        self.ln2 = nn.LayerNorm(n_emb)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


class GPTModel(nn.Module):
    """GPT-style transformer model"""
    def __init__(self, vocab_size, n_emb=384, n_head=6, n_layer=6, 
                 block_size=256, dropout=0.2):
        super().__init__()
        self.block_size = block_size
        
        # Token and position embeddings
        self.token_embedding_table = nn.Embedding(vocab_size, n_emb)
        self.position_embedding_table = nn.Embedding(block_size, n_emb)
        
        # Transformer blocks
        self.blocks = nn.Sequential(*[
            TransformerBlock(n_emb, n_head, block_size, dropout)
            for _ in range(n_layer)
        ])
        
        self.ln_f = nn.LayerNorm(n_emb)
        self.lm_head = nn.Linear(n_emb, vocab_size)
        
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        
        # Embeddings
        tok_emb = self.token_embedding_table(idx)  # (B, T, n_emb)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device))  # (T, n_emb)
        x = tok_emb + pos_emb  # (B, T, n_emb)
        
        # Forward through transformer
        x = self.blocks(x)  # (B, T, n_emb)
        x = self.ln_f(x)    # (B, T, n_emb)
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # Calculate loss if targets provided
        loss = None
        if targets is not None:
            B, T, C = logits.shape
            logits_flat = logits.view(B * T, C)
            targets_flat = targets.view(B * T)
            loss = F.cross_entropy(logits_flat, targets_flat)
        
        return logits, loss

    def generate(self, idx, max_new_tokens=100, temperature=1.0, top_k=None):
        """Generate text from context"""
        for _ in range(max_new_tokens):
            # Condition on last block_size tokens
            idx_cond = idx[:, -self.block_size:]
            
            # Get predictions
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            
            # Apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            
            # Sample next token
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        
        return idx


def train_tiny_model_pytorch(text_data, vocab_size, device='cuda' if torch.cuda.is_available() else 'cpu',
                            batch_size=64, epochs=3, learning_rate=3e-4):
    """Train the model on text data"""
    
    # Tokenize (simple char-level tokenization)
    chars = sorted(list(set(text_data)))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
    
    # Convert text to tokens
    data = torch.tensor(encode(text_data), dtype=torch.long)
    
    # Split into train/val
    train_size = int(0.9 * len(data))
    train_data = data[:train_size]
    val_data = data[train_size:]
    
    # Create model
    model = GPTModel(vocab_size=len(chars), n_emb=384, n_head=6, n_layer=6,
                    block_size=256, dropout=0.2).to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs * 100)
    
    print(f"Model: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Device: {device}")
    print(f"Training on {len(train_data):,} tokens, validating on {len(val_data):,} tokens\n")
    
    block_size = 256
    global_step = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        epoch_loss = 0
        
        for step in range(0, len(train_data) - block_size, batch_size):
            # Get batch
            idxs = torch.randint(0, len(train_data) - block_size, (batch_size,))
            x = torch.stack([train_data[i:i+block_size] for i in idxs]).to(device)
            y = torch.stack([train_data[i+1:i+block_size+1] for i in idxs]).to(device)
            
            # Forward
            logits, loss = model(x, y)
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            
            epoch_loss += loss.item()
            global_step += 1
            
            if step % 500 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Step {global_step}, Loss: {loss.item():.4f}")
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for step in range(0, min(len(val_data) - block_size, 500), batch_size):
                idxs = torch.randint(0, len(val_data) - block_size, (batch_size,))
                x = torch.stack([val_data[i:i+block_size] for i in idxs]).to(device)
                y = torch.stack([val_data[i+1:i+block_size+1] for i in idxs]).to(device)
                
                _, loss = model(x, y)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / max(1, (min(len(val_data) - block_size, 500) // batch_size))
        print(f"Epoch {epoch+1} Complete - Val Loss: {avg_val_loss:.4f}\n")
        
        # Save checkpoint
        torch.save(model.state_dict(), f"model_epoch_{epoch+1}.pt")
    
    print("Training complete!")
    return model, stoi, itos


def load_and_generate(model_path, stoi, itos, prompt="Once upon a time", 
                     max_tokens=100, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """Load a trained model and generate text"""
    
    model = GPTModel(vocab_size=len(stoi)).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
    
    context = torch.tensor([encode(prompt)], dtype=torch.long).to(device)
    
    with torch.no_grad():
        generated = model.generate(context, max_new_tokens=max_tokens, temperature=0.9, top_k=50)
    
    return decode(generated[0].tolist())


# Usage example:
if __name__ == "__main__":
    # Load your text file
    with open("data.txt", "r", encoding='utf-8') as f:
        text = f.read()
    
    vocab_size = len(set(text))
    
    # Train
    model, stoi, itos = train_tiny_model_pytorch(
        text, 
        vocab_size,
        batch_size=64,
        epochs=3,
        learning_rate=3e-4
    )
    
    # Generate
    output = load_and_generate("model_epoch_3.pt", stoi, itos, 
                              prompt="The future of AI", max_tokens=200)
    print("\n=== Generated Text ===")
    print(output)
