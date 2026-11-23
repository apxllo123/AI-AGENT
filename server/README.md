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

## Access control

`POST /chat`, `GET /memory`, `POST /memory/clear`, and `GET /conversations`
read and change your private data, so each one needs a token:

- Set `ACCESS_TOKEN` in `.env` to use your own token, or let the server make a
  temporary one for each run.
- The server prints the token on start. The web page asks for it once and keeps
  it in the browser. API clients send `Authorization: Bearer <token>` or
  `X-Auth-Token: <token>`.
- `ALLOWED_ORIGINS` names the browser origins that may call the API from another
  page. The bundled UI uses the same origin and needs no entry.
- `HOST` sets the interface. `0.0.0.0` is the default. Use `127.0.0.1` to answer
  local requests only.
- `GET /` and `GET /health` stay open.

Run the access control tests with `npm run test:server`.

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
