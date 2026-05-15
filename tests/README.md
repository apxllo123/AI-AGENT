# Tests

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../CONTRIBUTING.md">🤝 Contributing</a> •
  <a href="../SECURITY.md">🔐 Security</a> •
  <a href="../tokenizer/README.md">🔤 Tokenizer</a> •
  <a href="../python-service/README.md">🐍 Python Service</a>
</p>

---

This folder contains lightweight tests for AI-AGENT.

## Files

- `test_tokenizer.py` — checks tokenizer round-trip behavior.
- `test_agent_tools.py` — checks calculator, planner, memory, and favorite fact extraction.

## Run tests

```bash
pip install -r requirements.txt pytest
python -m pytest -q
```

If Flask is not installed, service-specific tests are skipped.
