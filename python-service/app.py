#!/usr/bin/env python3
"""AI-AGENT Python service.

Provides:
- /health for status
- /reply and /chat for chat responses
- a tiny trained-from-scratch model if artifacts/model.pt exists
- simple agent tools: memory, calculator, planner
- optional Ollama fallback/proxy when running on a stronger machine
"""
from __future__ import annotations

import ast
import json
import os
import pickle
import random
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from flask import Flask, jsonify, request

try:
    from flask_cors import CORS
except Exception:  # pragma: no cover - optional dependency
    CORS = None

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(ROOT_DIR))

app = Flask(__name__)
if CORS:
    CORS(app)

# Environment configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder")
USE_OLLAMA = os.getenv("USE_OLLAMA", "auto").lower()  # auto, true, false
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "180"))

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "agent_memory.json"

MODEL = None
BPE = None
MODEL_STATUS = "not_loaded"


def find_artifact(filename: str) -> Optional[Path]:
    candidates = [
        BASE_DIR / "artifacts" / filename,
        ROOT_DIR / "artifacts" / filename,
    ]
    return next((p for p in candidates if p.exists()), None)


def load_tiny_model():
    global MODEL, BPE, MODEL_STATUS
    model_path = find_artifact("model.pt")
    bpe_path = find_artifact("bpe.pkl")
    if not model_path or not bpe_path:
        MODEL_STATUS = "missing_artifacts"
        return
    try:
        import torch
        from model.huge_transformer import model_from_checkpoint

        with bpe_path.open("rb") as f:
            BPE = pickle.load(f)
        checkpoint = torch.load(model_path, map_location="cpu")
        MODEL = model_from_checkpoint(checkpoint, map_location="cpu")
        MODEL.eval()
        MODEL_STATUS = f"loaded:{model_path.relative_to(ROOT_DIR)}"
        print(f"✅ Tiny model loaded from {model_path}")
    except Exception as exc:  # keep API alive even if model load fails
        MODEL = None
        BPE = None
        MODEL_STATUS = f"load_error:{exc}"
        print(f"⚠️ Tiny model not loaded: {exc}")


load_tiny_model()


FALLBACK_RESPONSES = [
    "I can help with coding, planning, memory, and simple calculations. What do you want to build?",
    "Tell me the goal and I’ll break it into steps.",
    "My tiny model is still learning, but my agent tools are online.",
]


def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"notes": [], "facts": {}}


def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")


SAFE_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Num,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.FloorDiv,
    ast.USub,
    ast.UAdd,
    ast.Load,
)


def safe_calculate(expr: str) -> str:
    expr = expr.strip()
    if len(expr) > 120:
        raise ValueError("expression too long")
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, SAFE_AST_NODES):
            raise ValueError("only simple arithmetic is allowed")
    return str(eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, {}))


def call_ollama(message: str, history=None) -> Optional[str]:
    if USE_OLLAMA == "false":
        return None
    history = history or []
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are AI-AGENT, a helpful personal assistant. Be concise, safe, and practical.",
                },
                *history[-10:],
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=45)
        if res.ok:
            return (res.json().get("message") or {}).get("content", "").strip() or None
    except Exception:
        return None
    return None


def tiny_model_reply(message: str) -> Optional[str]:
    if MODEL is None or BPE is None:
        return None
    try:
        import torch

        prompt = f"User: {message}\nAssistant:"
        idx = torch.tensor([BPE.encode(prompt)], dtype=torch.long)
        with torch.no_grad():
            out = MODEL.generate(idx, max_new_tokens=MAX_NEW_TOKENS, temperature=0.8, top_k=40)[0]
        text = BPE.decode(out.tolist())
        reply = text.split("Assistant:")[-1].split("\nUser:")[0].strip()
        if len(reply) > 2:
            return reply
    except Exception as exc:
        print(f"Tiny generation error: {exc}")
    return None


def extract_memory_fact(message: str, memory):
    patterns = [
        (r"(?:my name is|call me)\s+(.+)", "name"),
        (r"i (?:like|love|enjoy)\s+(.+)", "likes"),
        (r"i (?:use|prefer)\s+(.+)", "prefers"),
    ]
    for regex, key in patterns:
        match = re.search(regex, message, flags=re.I)
        if match:
            value = match.group(1).strip(" .!")[:100]
            memory.setdefault("facts", {})[key] = value


def agent_reply(message: str, history=None) -> dict:
    message = (message or "").strip()
    if not message:
        return {"reply": "Message is required.", "source": "error"}

    memory = load_memory()
    lower = message.lower()

    # Memory tools
    if lower.startswith("remember ") or "remember that" in lower:
        note = re.sub(r"^remember(?: that)?\s*", "", message, flags=re.I).strip()
        memory.setdefault("notes", []).append(note)
        extract_memory_fact(note, memory)
        save_memory(memory)
        return {"reply": f"Saved to memory: {note}", "source": "tool:memory.write", "memory": memory}

    if lower in {"memory", "show memory", "what do you remember"} or "what do you remember" in lower:
        notes = memory.get("notes", [])
        facts = memory.get("facts", {})
        lines = []
        if facts:
            lines.append("Facts:")
            lines.extend(f"- {k}: {v}" for k, v in facts.items())
        if notes:
            lines.append("Notes:")
            lines.extend(f"- {n}" for n in notes[-20:])
        return {"reply": "\n".join(lines) if lines else "No memories saved yet.", "source": "tool:memory.read", "memory": memory}

    # Calculator tool
    calc_match = re.search(r"(?:calculate|calc|what is|what's)\s+([0-9+\-*/%().\s]+)\??$", message, flags=re.I)
    if calc_match:
        try:
            answer = safe_calculate(calc_match.group(1))
            return {"reply": f"The answer is {answer}.", "source": "tool:calculator"}
        except Exception as exc:
            return {"reply": f"I could not calculate that: {exc}", "source": "tool:calculator"}

    # Planner tool
    if lower.startswith("plan ") or "make a plan" in lower:
        goal = re.sub(r"^(plan|make a plan for|make a plan to)\s*", "", message, flags=re.I).strip() or message
        steps = [
            f"Define success for: {goal}",
            "List the smallest next 3 tasks.",
            "Do the easiest task for 15 minutes.",
            "Review, save what you learned, then repeat.",
        ]
        return {"reply": "Here’s a plan:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)), "source": "tool:planner"}

    # Optional stronger model
    ollama = call_ollama(message, history=history)
    if ollama:
        extract_memory_fact(message, memory)
        save_memory(memory)
        return {"reply": ollama, "source": f"ollama:{OLLAMA_MODEL}", "memory": memory}

    # Tiny from-scratch model
    tiny = tiny_model_reply(message)
    if tiny:
        extract_memory_fact(message, memory)
        save_memory(memory)
        return {"reply": tiny, "source": "tiny_from_scratch_model", "memory": memory}

    # Last-resort fallback
    return {"reply": random.choice(FALLBACK_RESPONSES), "source": "fallback", "memory": memory}


@app.get("/")
def home():
    return jsonify(
        {
            "status": "ok",
            "service": "AI-AGENT python-service",
            "tiny_model": MODEL is not None,
            "model_status": MODEL_STATUS,
            "ollama_model": OLLAMA_MODEL,
            "endpoints": ["/health", "/reply", "/chat", "/memory"],
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "tiny_model": MODEL is not None, "model_status": MODEL_STATUS})


@app.post("/reply")
@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    result = agent_reply(str(data.get("message", "")), history=data.get("history", []))
    status = 400 if result.get("source") == "error" else 200
    return jsonify(result), status


@app.get("/memory")
def memory_get():
    return jsonify(load_memory())


@app.post("/memory/clear")
def memory_clear():
    save_memory({"notes": [], "facts": {}})
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))
    print(f"🚀 AI-AGENT Python service running on http://0.0.0.0:{port}")
    print(f"Tiny model status: {MODEL_STATUS}")
    app.run(host="0.0.0.0", port=port, debug=False)
