# Python Service

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../model/README.md">🧠 Model</a> •
  <a href="../tokenizer/README.md">🔤 Tokenizer</a> •
  <a href="../server/README.md">🌐 Server</a>
</p>

---

This folder contains the Flask API for AI-AGENT's tiny model and agent tools.

## Files

- `app.py` — Flask API, tiny model loading, memory, calculator, planner, and optional Ollama routing.
- `requirements.txt` — Python service dependencies.
- `requirements-dev.txt` — dev/test dependencies.
- `artifacts/` — where `model.pt` and `bpe.pkl` are copied after training.
- `model/` and `tokenizer/` — service-local copies for deployment compatibility.

## Endpoints

```text
GET  /          service info
GET  /health    status and tiny model load state
POST /chat      chat endpoint
POST /reply     same as /chat
GET  /memory    read memory
POST /memory/clear clear memory
```

## Run it

From the repo root:

```bash
python python-service/app.py
```

Default port:

```text
http://localhost:8081
```

## Test it

```bash
curl -X POST http://127.0.0.1:8081/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"calculate 9*9"}'
```
