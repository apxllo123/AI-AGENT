# Data

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../tokenizer/README.md">🔤 Tokenizer</a> •
  <a href="../model/README.md">🧠 Model</a> •
  <a href="../SECURITY.md">🔐 Security</a>
</p>

---

This folder stores training text and local runtime memory.

## Files

- `tiny_data.txt` — main chat-style training examples.
- `facts.txt` — extra simple facts for training.

Runtime files may also appear here, but should not be committed:

- `agent_memory.json`
- `jarvis_memory.json`
- `conversations.json`

## Best training format

Use clean examples like this:

```text
User: explain what an ai agent is
Assistant: An AI agent is software that can plan, use tools, remember useful facts, and act toward a goal.
```

## Improve the model

Add better examples, then train again:

```bash
python train.py --steps 1500
```

Do not put private information, passwords, API keys, or sensitive conversations in training data.
