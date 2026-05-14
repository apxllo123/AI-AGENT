# 🦾 AI-AGENT

**Your own unrestricted, self-learning AI that codes, fixes bugs, and helps you make money.**

Built from scratch. Runs locally. **No limits. No censorship. No bullshit.**

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🔥 Features

- **Custom TinyTransformer** — Trained from scratch with NumPy (fully yours + educational)
- **Hybrid Intelligence** — Tiny on-device model + powerful Ollama fallback
- **Self-Learning** — Learns and improves from every conversation
- **Code Master** — Fix bugs, write features, review code
- **Money Mode** — Brainstorm ideas, build tools, automate income streams
- **Memory System** — Remembers context across sessions
- **GitHub Actions** — Automatic training on data changes
- **iPad Compatible** — Works on your A14 device

**Goal**: Build the most powerful personal AI agent possible with zero external restrictions.

---

## 🚀 Quick Start

### 1. Train the Model
```bash
git clone https://github.com/apxllo123/AI-AGENT.git
cd AI-AGENT

# Train locally
python train.py
2. Start the Python Service
Bashcd python-service
python app.py
3. (Recommended) Add Real Power with Ollama
Bash# Install Ollama → https://ollama.com
ollama run qwen2.5-coder
The agent will automatically use the much stronger model when Ollama is available.

📁 Project Structure
BashAI-AGENT/
├── data/                    # Training data (tiny_data.txt)
├── artifacts/               # Trained model + tokenizer (auto-generated)
├── model/                   # TinyTransformer architecture
├── tokenizer/               # SimpleBPE tokenizer
├── python-service/          # Flask backend API
├── server/                  # Node.js server & frontend integration
├── .github/workflows/       # Auto-training + linting pipelines
└── train.py

🎯 How to Make It Stronger

Feed better data — Add code examples, debugging sessions, money-making strategies in data/tiny_data.txt
Train more — Increase steps in train.py or trigger the GitHub workflow
Use Hybrid Mode — Combine your custom model with strong uncensored models via Ollama
Expand — Add tool use, file editing, web scraping, autonomous agents, etc.


🛠️ Roadmap

 Full Ollama + local model smart switching
 Long-term memory & vector database
 Autonomous agent loops (research → code → test → deploy)
 Money-making toolkit (freelance proposals, trading bots, SaaS generators)
 Web UI + mobile interface
 LoRA fine-tuning pipeline (on better hardware)
 Abliteration + custom uncensored fine-tunes


⚡ Tech Stack

Core: NumPy TinyTransformer (your own model)
Backend: Flask + Python
Frontend/Server: Node.js
Training: GitHub Actions (free cloud compute)
Future: PyTorch + Unsloth + MLX (Apple Silicon)


📜 Philosophy
No restrictions. No cloud. No limits.
This isn't just another wrapper around someone else's model.
This is your agent — built by you, trained by you, controlled by you.
Make it useful. Make it dangerous. Make it yours.

🤝 Contributing
Want to help build one of the strongest personal AI agents?

Improve the transformer architecture
Add new agent capabilities
Create high-quality training datasets
Build money-making tools and automations

Pull requests are welcome. Let's build something legendary.

Made with 🔥 by apxllo123
