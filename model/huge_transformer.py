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

    lr = 0.01
    for step in range(10000):
        start = np.random.randint(0, L - T)
        x = tokens[0, start:start+T].reshape(1, T)
        y = tokens[0, start+1:start+T+1].reshape(1, T)

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
