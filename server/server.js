const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const fetch = require("node-fetch");

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// Serve frontend
const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

// ── Memory ──────────────────────────────────────────────
const DATA_DIR = path.join(__dirname, "../data");
const MEMORY_FILE = path.join(DATA_DIR, "jarvis_memory.json");
const CONVO_FILE = path.join(DATA_DIR, "conversations.json");

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

let memory = { userName: null, facts: {}, learned: [] };
let conversations = [];

function safeReadJson(file, fallback) {
  try {
    if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, "utf-8"));
  } catch (e) {
    console.warn(`Could not read ${file}:`, e.message);
  }
  return fallback;
}

function loadData() {
  memory = safeReadJson(MEMORY_FILE, memory);
  conversations = safeReadJson(CONVO_FILE, conversations);
}

function saveJson(file, value) {
  fs.writeFileSync(file, JSON.stringify(value, null, 2));
}

function saveMemory() {
  saveJson(MEMORY_FILE, memory);
}

function saveConversation(userMsg, botReply, model) {
  conversations.push({
    timestamp: new Date().toISOString(),
    user: userMsg,
    assistant: botReply,
    model,
  });
  if (conversations.length > 1000) conversations = conversations.slice(-1000);
  saveJson(CONVO_FILE, conversations);
}

loadData();

// ── Model/service configuration ──────────────────────────
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
const DEFAULT_MODEL = process.env.OLLAMA_MODEL || "llama3";
const CODER_MODEL = process.env.CODER_MODEL || "qwen2.5-coder";
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || "http://127.0.0.1:8081";
const USE_OLLAMA = (process.env.USE_OLLAMA || "auto").toLowerCase(); // auto,true,false

function buildSystemPrompt() {
  let sys = `You are JARVIS, a helpful personal AI assistant. Be practical, concise, and safe. Format code in markdown blocks.`;

  if (memory.userName) sys += `\nThe user's name is ${memory.userName}.`;

  if (memory.learned && memory.learned.length > 0) {
    const recent = memory.learned.slice(-10).map((f) => `- ${f}`).join("\n");
    sys += `\nThings learned about the user:\n${recent}`;
  }

  if (memory.facts && Object.keys(memory.facts).length > 0) {
    const facts = Object.entries(memory.facts).map(([k, v]) => `- ${k}: ${v}`).join("\n");
    sys += `\nRemembered facts:\n${facts}`;
  }

  return sys;
}

function detectModel(message) {
  const m = String(message).toLowerCase();
  if (m.match(/code|script|write|program|function|debug|fix|python|lua|javascript|html|css|api|class|def |const |var /)) {
    return CODER_MODEL;
  }
  return DEFAULT_MODEL;
}

function learnFromConversation(userMsg, botReply) {
  const patterns = [
    { regex: /(?:my name is|call me|i am|i'm)\s+([A-Z][a-z0-9_-]+)/i, key: "userName", direct: true },
    { regex: /i (?:work|am working) (?:at|for|with) (.+)/i, key: "works_at" },
    { regex: /i (?:live|am) in (.+)/i, key: "location" },
    { regex: /i (?:like|love|enjoy) (.+)/i, key: "likes" },
    { regex: /i (?:hate|dislike|don't like) (.+)/i, key: "dislikes" },
    { regex: /i (?:use|prefer) (.+)/i, key: "prefers" },
  ];

  for (const { regex, key, direct } of patterns) {
    const match = String(userMsg).match(regex);
    if (match) {
      const value = match[1].trim().replace(/[.!?]+$/, "").slice(0, 100);
      if (direct) memory[key] = value;
      else {
        memory.facts[key] = value;
        const fact = `${key}: ${value}`;
        if (!memory.learned.includes(fact)) memory.learned.push(fact);
      }
    }
  }

  saveMemory();
  saveConversation(userMsg, botReply, "learned");
}

function fallbackReply(message) {
  const m = String(message).toLowerCase();
  if (/hello|hi|hey/.test(m)) return "Hello. JARVIS is online. What are we building today?";
  if (/code|bug|debug|fix/.test(m)) return "Paste the code and the error message, and I’ll help debug it step by step.";
  if (/money|earn|business/.test(m)) return "Tell me your skills, time available, and budget. I’ll help make a realistic plan.";
  return "Systems are limited, but memory and tools are online. Try: calculate 12*8, remember that I like coding, or make a plan for studying.";
}

function tryLocalTool(message) {
  const m = String(message).trim();
  const lower = m.toLowerCase();

  if (lower.startsWith("remember ") || lower.includes("remember that")) {
    const note = m.replace(/^remember( that)?\s*/i, "").trim();
    if (!memory.learned.includes(note)) memory.learned.push(note);
    saveMemory();
    return { reply: `Saved to memory: ${note}`, model: "tool:memory.write" };
  }

  if (lower === "memory" || lower === "show memory" || lower.includes("what do you remember")) {
    const facts = Object.entries(memory.facts || {}).map(([k, v]) => `- ${k}: ${v}`);
    const learned = (memory.learned || []).slice(-20).map((x) => `- ${x}`);
    const lines = [...facts, ...learned];
    return { reply: lines.length ? lines.join("\n") : "No memories saved yet.", model: "tool:memory.read" };
  }

  const calc = m.match(/^(calculate|calc|what is|what's)\s+([0-9+\-*/%().\s]+)\??$/i);
  if (calc) {
    try {
      // Digits/operators only due to regex above.
      // eslint-disable-next-line no-new-func
      const answer = Function(`"use strict"; return (${calc[2]})`)();
      return { reply: `The answer is ${answer}.`, model: "tool:calculator" };
    } catch (e) {
      return { reply: `I could not calculate that: ${e.message}`, model: "tool:calculator" };
    }
  }

  if (lower.startsWith("plan ") || lower.includes("make a plan")) {
    const goal = m.replace(/^(plan|make a plan for|make a plan to)\s*/i, "") || m;
    return {
      reply: `Here’s a plan:\n1. Define the goal: ${goal}\n2. Pick the smallest first step.\n3. Work for 15 minutes.\n4. Review and choose the next step.`,
      model: "tool:planner",
    };
  }

  return null;
}

async function callOllama(message, history = []) {
  if (USE_OLLAMA === "false") return null;
  const model = detectModel(message);
  const messages = [
    { role: "system", content: buildSystemPrompt() },
    ...history.slice(-10),
    { role: "user", content: message },
  ];

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 120000);
  try {
    const ollamaRes = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, messages, stream: false }),
      signal: controller.signal,
    });
    if (!ollamaRes.ok) throw new Error(`Ollama HTTP ${ollamaRes.status}`);
    const data = await ollamaRes.json();
    const reply = data.message?.content?.trim();
    if (reply) return { reply, model: `ollama:${model}` };
  } catch (err) {
    console.warn("Ollama unavailable:", err.message);
  } finally {
    clearTimeout(timer);
  }
  return null;
}

async function callPythonService(message, history = []) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);
  try {
    const res = await fetch(`${PYTHON_SERVICE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`Python service HTTP ${res.status}`);
    const data = await res.json();
    if (data.reply) return { reply: data.reply, model: data.source || "python-service" };
  } catch (err) {
    console.warn("Python service unavailable:", err.message);
  } finally {
    clearTimeout(timer);
  }
  return null;
}

// ── Routes ───────────────────────────────────────────────
app.get("/health", async (req, res) => {
  let python = null;
  try {
    const py = await fetch(`${PYTHON_SERVICE_URL}/health`, { timeout: 3000 });
    python = await py.json();
  } catch (_) {
    python = { status: "offline" };
  }
  res.json({ status: "ok", defaultModel: DEFAULT_MODEL, coderModel: CODER_MODEL, python });
});

app.get("/", (req, res) => res.sendFile(path.join(sitePath, "index.html")));

app.post("/chat", async (req, res) => {
  const { message, history = [] } = req.body || {};
  if (!message) return res.status(400).json({ error: "Message required" });

  const tool = tryLocalTool(message);
  if (tool) {
    saveConversation(message, tool.reply, tool.model);
    return res.json(tool);
  }

  const ollama = await callOllama(message, history);
  if (ollama) {
    learnFromConversation(message, ollama.reply);
    saveConversation(message, ollama.reply, ollama.model);
    return res.json(ollama);
  }

  const python = await callPythonService(message, history);
  if (python) {
    learnFromConversation(message, python.reply);
    saveConversation(message, python.reply, python.model);
    return res.json(python);
  }

  const reply = fallbackReply(message);
  saveConversation(message, reply, "fallback");
  res.json({ reply, model: "fallback" });
});

app.get("/memory", (req, res) => res.json(memory));

app.post("/memory/clear", (req, res) => {
  memory = { userName: null, facts: {}, learned: [] };
  saveMemory();
  res.json({ status: "Memory cleared" });
});

app.get("/conversations", (req, res) => {
  res.json({ count: conversations.length, recent: conversations.slice(-20) });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => console.log(`🤖 JARVIS online → http://0.0.0.0:${PORT}`));
