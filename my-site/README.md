# Web UI

<p align="center">
  <a href="../README.md">🏠 Overview</a> •
  <a href="../COLAB_IPAD_SETUP.md">📱 iPad/Colab</a> •
  <a href="../server/README.md">🌐 Server</a> •
  <a href="../python-service/README.md">🐍 Python Service</a> •
  <a href="../SECURITY.md">🔐 Security</a>
</p>

---

This folder contains the iPad-friendly JARVIS web interface.

## Files

- `index.html` — main app UI.
- `jarvis.html` — redirect to `index.html` for older links.
- `css/jarvis.css` — responsive JARVIS styling.
- `js/chat.js` — frontend chat logic.

## Features

- mobile/iPad safe-area support,
- animated JARVIS-style background,
- quick action buttons,
- memory status display,
- model/source badge,
- markdown-style code block rendering.

## Run it

The UI is served by the Node server:

```bash
npm install
npm start
```

Then open:

```text
http://localhost:8080
```
