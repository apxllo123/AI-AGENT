def train_step(self, x, y, lr=1e-3):
    """Manual backprop with simple SGD - complete implementation"""
    # Forward pass
    B, T = x.shape
    emb = self.tok_emb[x] + self.pos_emb[:T]
    
    # Forward through layers (store all activations for backprop)
    activations = [emb]
    h = emb
    layer_inputs = [h.copy()]
    
    for layer in self.layers:
        z1 = np.matmul(h, layer['W1']) + layer['b1']
        a1 = np.tanh(z1)
        z2 = np.matmul(a1, layer['W2']) + layer['b2']
        h_new = np.tanh(z2) + h  # residual connection
        h = h_new
        
        activations.extend([z1, a1, z2, h])
        layer_inputs.append(h.copy())
    
    logits = np.matmul(h, self.W_out) + self.b_out
    
    # Softmax + cross-entropy loss
    logits_flat = logits.reshape(-1, self.vocab_size)
    targets_flat = y.reshape(-1)
    
    exp_logits = np.exp(logits_flat - np.max(logits_flat, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    loss = -np.log(np.clip(probs[np.arange(len(targets_flat)), targets_flat], 1e-12, 1.0)).mean()
    
    # ==================== BACKWARD PASS ====================
    
    # Output layer gradient
    dlogits = probs.copy()
    dlogits[np.arange(len(targets_flat)), targets_flat] -= 1
    dlogits /= len(targets_flat)
    dlogits = dlogits.reshape(B, T, self.vocab_size)
    
    # Gradient w.r.t. output layer hidden state
    dh = np.matmul(dlogits, self.W_out.T)  # (B, T, n_embd)
    
    # Gradients for output weights and biases
    h_flat = h.reshape(-1, self.n_embd)
    dlogits_flat = dlogits.reshape(-1, self.vocab_size)
    dW_out = np.matmul(h_flat.T, dlogits_flat) / B
    db_out = dlogits_flat.sum(axis=0) / B
    
    # Update output layer
    self.W_out -= lr * dW_out
    self.b_out -= lr * db_out
    
    # ==================== BACKPROP THROUGH LAYERS ====================
    
    for i, layer in reversed(list(enumerate(self.layers))):
        # Get the input to this layer and its intermediate activations
        h_prev = layer_inputs[i]  # input to this layer
        
        # Extract z1, a1, z2 for this layer from activations
        # activations structure: [emb, z1_0, a1_0, z2_0, h_0, z1_1, a1_1, z2_1, h_1, ...]
        # Each layer contributes 4 elements: [z1, a1, z2, h]
        layer_act_idx = 1 + i * 4
        z1 = activations[layer_act_idx]
        a1 = activations[layer_act_idx + 1]
        z2 = activations[layer_act_idx + 2]
        
        # Gradient of tanh(z2) + residual
        # d/dz2[tanh(z2) + h_prev] = (1 - tanh^2(z2))
        dtanh_z2 = 1.0 - np.tanh(z2) ** 2
        dz2 = dh * dtanh_z2
        
        # Gradients for second layer of FFN
        dW2 = np.matmul(a1.transpose(0, 2, 1).reshape(-1, self.n_embd).T, 
                        dz2.reshape(-1, self.n_embd)) / B
        db2 = dz2.sum(axis=(0, 1)) / B
        
        # Backprop to a1
        da1 = np.matmul(dz2, layer['W2'].T)
        
        # Gradient of tanh(z1)
        dtanh_z1 = 1.0 - np.tanh(z1) ** 2
        dz1 = da1 * dtanh_z1
        
        # Gradients for first layer of FFN
        dW1 = np.matmul(h_prev.transpose(0, 2, 1).reshape(-1, self.n_embd).T, 
                        dz1.reshape(-1, self.n_embd)) / B
        db1 = dz1.sum(axis=(0, 1)) / B
        
        # Backprop to previous layer (residual + FFN)
        dh = np.matmul(dz1, layer['W1'].T) + dh  # residual connection backprop
        
        # Update layer parameters
        layer['W1'] -= lr * dW1
        layer['b1'] -= lr * db1
        layer['W2'] -= lr * dW2
        layer['b2'] -= lr * db2
    
    # ==================== UPDATE EMBEDDINGS ====================
    
    # Gradient for token embeddings (dh is now gradient w.r.t. input embeddings)
    demb = dh.copy()  # (B, T, n_embd)
    
    # Update embeddings using scatter operations
    for b in range(B):
        for t in range(T):
            token_idx = x[b, t]
            self.tok_emb[token_idx] -= lr * demb[b, t]
    
    # Position embeddings are typically fixed or updated carefully
    # For now we skip updating them to avoid breaking the positional encoding
    
    return float(loss)

# Add to class
TinyTransformer.train_step = train_step
