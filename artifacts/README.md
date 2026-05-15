# Artifacts

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../model/README.md">🧠 Model</a> •
  <a href="../tokenizer/README.md">🔤 Tokenizer</a>
</p>

---

Training writes model/tokenizer files here:

- `model.pt` — tiny Transformer checkpoint.
- `bpe.pkl` — tokenizer.

Run:

```bash
python train.py --quick
```

The same files are copied to `python-service/artifacts/` so the Flask service can load them.

Legacy `model.pkl` files were removed because the current code uses PyTorch `.pt` checkpoints.
