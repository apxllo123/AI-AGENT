# Model

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../tokenizer/README.md">🔤 Tokenizer</a> •
  <a href="../python-service/README.md">🐍 Python Service</a> •
  <a href="../server/README.md">🌐 Server</a>
</p>

---

This folder contains the tiny GPT-style Transformer architecture used by AI-AGENT.

## File

- `huge_transformer.py` — the tiny Transformer model, training helper, checkpoint helpers, and generation method.

## Main pieces

- `TinyGPTConfig` — model settings such as vocab size, embedding size, heads, layers, and context length.
- `CausalSelfAttention` — masked self-attention so the model predicts the next token without seeing the future.
- `TransformerBlock` — attention + feed-forward block.
- `GPTModel` — full tiny language model.
- `train_tiny_model_pytorch()` — training loop used by `train.py`.
- `model_from_checkpoint()` — loads `model.pt` for inference.

## Why it is tiny

This model is for learning and experimenting. It is not meant to compete with large models. The agent becomes useful by combining this model with tools, memory, and optional Ollama fallback.

## Train it

```bash
python train.py --quick
```

Better training:

```bash
python train.py --steps 1500
```
