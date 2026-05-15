# Tokenizer

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../model/README.md">🧠 Model</a> •
  <a href="../python-service/README.md">🐍 Python Service</a> •
  <a href="../server/README.md">🌐 Server</a>
</p>

---

This folder contains the educational tokenizer used by AI-AGENT.

## File

- `transformer.py` — `SimpleBPE`, a small BPE-style tokenizer.

## What it does

The tokenizer converts text into token IDs before training/inference, then converts generated token IDs back into text.

Important behavior:

- preserves spaces and newlines,
- keeps base characters so new text does not become all unknown tokens,
- supports `<unk>`, `<bos>`, and `<eos>` special tokens,
- is intentionally simple so you can understand and modify it.

## Quick test

```bash
python tokenizer/transformer.py
```

## Used by

- `train.py` during training,
- `python-service/app.py` during chat inference,
- tests in `tests/test_tokenizer.py`.
