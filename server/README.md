# Node Server

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../python-service/README.md">🐍 Python Service</a> •
  <a href="../my-site/README.md">🎨 Web UI</a> •
  <a href="../SECURITY.md">🔐 Security</a>
</p>

---

This folder contains the Node/Express web server.

## Files

- `server.js` — serves the web UI and routes chat requests.
- `reply.py` — CLI helper for testing the Python agent reply logic.

## Routing order

When a user sends a message, the server tries:

1. local tools such as memory, calculator, and planner,
2. Ollama, if available,
3. Python service at `PYTHON_SERVICE_URL`,
4. simple fallback response.

## Run it

From the repo root:

```bash
npm install
npm start
```

Default web URL:

```text
http://localhost:8080
```

## Run full app

```bash
./start_agent.sh
```

This starts both the Python service and the Node web UI.
