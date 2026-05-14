# 🦾 AI-AGENT

**Your own unrestricted, self-learning AI that codes, fixes bugs, and helps you make money.**

Built from scratch. Runs locally. No limits. No censorship. No bullshit.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🔥 Features

- **Custom TinyTransformer** — Trained from scratch with NumPy (educational + fully yours)
- **Hybrid Intelligence** — Tiny model on-device + powerful Ollama fallback
- **Self-Learning** — Improves from every conversation
- **Code Master** — Fix bugs, write features, review code
- **Money Mode** — Brainstorm ideas, build tools, automate income streams
- **Memory System** — Remembers context across sessions
- **GitHub Actions** — Auto-trains on data changes
- **iPad Compatible** — Works on your A14 device

**Goal**: Build the most powerful personal AI agent possible with zero external restrictions.

---

## 🚀 Quick Start

### 1. Train the Model
```bash
# Clone & setup
git clone https://github.com/apxllo123/AI-AGENT.git
cd AI-AGENT

# Train (runs on GitHub Actions too)
python train.py
2. Start the Python Service
Bashcd python-service
python app.py
3. (Recommended) Add Real Power with Ollama
Bash# Install Ollama → https://ollama.com
ollama run qwen2.5-coder
The agent will automatically use the strong model when available.

📁 Project Structure
textAI-AGENT/
├── data/                  # Your training corpus (tiny_data.txt)
├── artifacts/             # Trained model + tokenizer (auto-generated)
├── model/                 # TinyTransformer architecture
├── tokenizer/             # SimpleBPE tokenizer
├── python-service/        # Flask backend API
├── server/                # Node.js frontend / integration layer
├── .github/workflows/     # Auto training + linting
└── train.py

🎯 How to Make It Stronger

Feed it better data — Add code examples, money-making strategies, debugging sessions into data/tiny_data.txt
Train more — Increase steps in train.py or trigger the GitHub workflow
Hybrid Mode — Use a strong uncensored model (Qwen, Dolphin, etc.) via Ollama
Expand — Add CrewAI agents, tool use, file editing, web scraping, etc.


🛠️ Roadmap

 Full Ollama + local model switching
 Long-term memory & vector database
 Autonomous agent loops (research → code → test)
 Money-making toolkit (freelance proposals, trading bots, SaaS generators)
 Web UI + mobile interface
 LoRA fine-tuning pipeline (when on better hardware)
 Abliteration + custom fine-tunes


⚡ Tech Stack

Core: NumPy TinyTransformer (your own model)
Backend: Flask + Python
Frontend: Node.js / your choice
Training: GitHub Actions (free compute)
Future: PyTorch + Unsloth + MLX (Apple Silicon)


📜 Philosophy
No restrictions. No cloud. No limits.
This isn't just another wrapper around someone else's model.
This is your agent — built by you, trained by you, controlled by you.
Make it useful. Make it dangerous. Make it yours.

🤝 Contributing
Want to help make the strongest personal AI agent?

Improve the transformer architecture
Add new agent capabilities
Create better training datasets
Build money-making tools

Pull requests welcome. Let's build something legendary.

Made with 🔥 by apxllo123
