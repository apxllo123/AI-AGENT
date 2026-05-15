# 🦾 AI-AGENT

**Your own self-learning personal AI agent that codes, fixes bugs, remembers context, makes plans, and helps you build useful projects.**

Built around a tiny model you train from scratch, wrapped with practical agent tools, and designed to work from an **iPad-friendly web app**.

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![iPad](https://img.shields.io/badge/iPad-compatible-purple)

---

## 🔥 Features

- **Custom TinyTransformer** — A small GPT-style Transformer trained from scratch with PyTorch. Fully educational and fully yours.
- **Agentic Tool Layer** — Memory, calculator, planning, and routing logic make the assistant useful even while the tiny model is still learning.
- **Hybrid Intelligence** — Uses local tools first, optional Ollama for stronger answers, then your tiny model, then a fallback.
- **Self-Learning Memory** — Saves useful facts and notes across sessions.
- **Code Helper Mode** — Helps debug code, write features, review snippets, and explain errors step by step.
- **Builder / Money Mode** — Brainstorms product ideas, freelance plans, automation tools, and practical ways to build value.
- **GitHub Actions** — Optional automatic training/checks when data or code changes.
- **iPad Compatible** — Use the web UI on an iPad 10th gen. Train/run in Colab, Codespaces, Replit, or a cloud server.
- **Local-First Design** — Can run on your own machine/server, with optional cloud notebooks for iPad-only workflows.

**Goal:** Build a powerful personal AI agent that you understand, control, improve, and customize over time.

> Reality check: a tiny model trained from scratch will not be ChatGPT-level. This project is about learning how models work, then making the full agent useful with tools, memory, and optional stronger model backends like Ollama.

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/apxllo123/AI-AGENT.git
cd AI-AGENT
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the tiny model

Fast smoke test:

```bash
python train.py --quick
```

Better local training:

```bash
python train.py --steps 1500
```

Training creates:

```text
artifacts/model.pt
artifacts/bpe.pkl
python-service/artifacts/model.pt
python-service/artifacts/bpe.pkl
```

### 4. Start the app

Option A — start Python service and web UI together:

```bash
npm install
./start_agent.sh
```

Option B — start them separately:

Terminal 1:

```bash
python python-service/app.py
```

Terminal 2:

```bash
npm install
npm start
```

Open:

```text
http://localhost:8080
```

---

## 📱 iPad 10th Gen / iPad-Only Setup

If you only have an iPad, use **Google Colab**, **GitHub Codespaces**, **Replit**, or another cloud runtime.

For the step-by-step iPad guide, open:

```text
COLAB_IPAD_SETUP.md
```

Basic Colab flow:

```bash
!git clone https://github.com/apxllo123/AI-AGENT.git
%cd AI-AGENT
!pip install -r requirements.txt
!python train.py --quick
!python python-service/app.py
```

To open the app/API from Safari, use a public tunnel or hosted environment such as:

- ngrok
- Cloudflare Tunnel
- GitHub Codespaces port forwarding
- Replit
- Render
- Railway

---

## 🧠 Optional: Add Real Power with Ollama

Your tiny model is educational. For stronger answers, run an Ollama model on a computer/server:

```bash
ollama pull qwen2.5-coder
OLLAMA_MODEL=qwen2.5-coder npm start
```

Recommended models:

```bash
ollama pull qwen2.5-coder
ollama pull llama3
```

The Node server tries responses in this order:

1. built-in agent tools,
2. Ollama if available,
3. Python tiny-model service,
4. simple fallback response.

---

## 🧪 Agent Commands to Try

```text
calculate 12 * 8 + 4
remember that my favorite color is blue
what do you remember
make a plan for studying tonight
hello
help me debug this Python code
how can I make money with an AI tool?
```

The tools work even if the tiny trained-from-scratch model is still weak.

---

## 📁 Project Structure

```text
AI-AGENT/
├── data/                    # Training data and saved memory
├── artifacts/               # Trained model + tokenizer artifacts
├── model/                   # TinyTransformer / GPT-style architecture
├── tokenizer/               # SimpleBPE educational tokenizer
├── python-service/          # Flask backend API for tiny model + tools
├── server/                  # Node.js server and frontend integration
├── my-site/                 # iPad-friendly web UI
├── .github/workflows/       # Auto-training and linting pipelines
├── train.py                 # Training script
├── start_agent.sh           # Starts backend + web server together
├── requirements.txt         # Python dependencies
└── package.json             # Node dependencies/scripts
```

---

## 🎯 How to Make It Stronger

### 1. Feed better data

Add high-quality examples to:

```text
data/tiny_data.txt
```

Use this format:

```text
User: explain what an ai agent is
Assistant: An AI agent is software that can plan, use tools, remember useful facts, and act toward a goal.
```

Good data ideas:

- coding questions and answers,
- debugging examples,
- business/product planning examples,
- personal assistant conversations,
- tool-use examples,
- explanations in the style you want.

### 2. Train longer

```bash
python train.py --steps 5000 --n-embd 192 --n-layer 4 --n-head 4
```

### 3. Use Hybrid Mode

Combine your custom tiny model with stronger local models through Ollama.

### 4. Expand the agent

Add more tools, such as:

- file reading/writing,
- web search,
- calendar/tasks,
- code execution sandbox,
- vector database memory,
- GitHub issue/PR automation,
- research → plan → code → test loops.

---

## 🛠️ Roadmap

- [x] iPad-friendly web UI
- [x] Tiny Transformer training script
- [x] Memory system
- [x] Calculator tool
- [x] Planner tool
- [x] Ollama fallback support
- [x] GitHub Actions training/check pipeline
- [ ] Long-term memory with embeddings/vector database
- [ ] Better autonomous agent loop: research → code → test → improve
- [ ] File editing and project workspace tools
- [ ] Web search tool
- [ ] Money-making toolkit: freelance proposals, SaaS idea generator, automation builder
- [ ] Native iPad app wrapper
- [ ] LoRA/fine-tuning pipeline for stronger open-source models
- [ ] MLX/Apple Silicon optimization

---

## ⚡ Tech Stack

- **Core model:** Tiny GPT-style Transformer trained from scratch with PyTorch
- **Tokenizer:** Simple educational BPE tokenizer
- **Backend:** Flask + Python
- **Frontend/server:** Node.js + Express
- **UI:** HTML/CSS/JavaScript, designed for mobile/iPad
- **Training:** Local Python, Colab, Codespaces, or GitHub Actions
- **Optional stronger model:** Ollama with models like `qwen2.5-coder` or `llama3`
- **Future:** PyTorch, Unsloth, MLX, vector databases, tool plugins

---

## ⚙️ Environment Variables

### Node server

```bash
PORT=8080
PYTHON_SERVICE_URL=http://127.0.0.1:8081
USE_OLLAMA=auto          # auto, true, false
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
CODER_MODEL=qwen2.5-coder
```

### Python service

```bash
PORT=8081
USE_OLLAMA=auto
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder
MAX_NEW_TOKENS=180
```

You can copy `.env.example` as a starting point.

---

## 📜 Philosophy

This is not just another chat wrapper.

This is your AI project:

- trained by you,
- modified by you,
- extended by you,
- controlled by you,
- improved over time with your own data and tools.

Build it. Break it. Fix it. Train it. Make it useful. Make it yours.

Use it responsibly: do not use this project to break laws, invade privacy, generate malware, or automate harmful actions.

---

## 🤝 Contributing

Want to help build a stronger personal AI agent?

Good contributions:

- improve the Transformer architecture,
- improve the tokenizer,
- add new safe agent tools,
- create high-quality training datasets,
- improve the iPad/mobile UI,
- add tests and benchmarks,
- build useful automation features.

Pull requests are welcome. Let’s build something legendary.

---

## ✅ What Changed in v0.2

- Fixed Transformer attention shape issues.
- Replaced incompatible `model.pkl` loading with `model.pt` checkpoints.
- Added a tokenizer that preserves spaces and newlines.
- Made `train.py` configurable and Colab/iPad friendly.
- Added `/chat`, `/reply`, `/health`, and memory endpoints to the Python service.
- Added Node fallback to the Python tiny-model service.
- Added local tools: memory, calculator, planner.
- Updated requirements and npm scripts.
- Added `COLAB_IPAD_SETUP.md`, `.env.example`, `.gitignore`, and `start_agent.sh`.

---

Made with 🔥 by **apxllo123**
