const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());

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

function loadData() {
  try {
    if (fs.existsSync(MEMORY_FILE))
      memory = JSON.parse(fs.readFileSync(MEMORY_FILE, "utf-8"));
  } catch (e) {}
  try {
    if (fs.existsSync(CONVO_FILE))
      conversations = JSON.parse(fs.readFileSync(CONVO_FILE, "utf-8"));
  } catch (e) {}
}

function saveMemory() {
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
}

function saveConversation(userMsg, botReply) {
  conversations.push({
    timestamp: new Date().toISOString(),
    user: userMsg,
    assistant: botReply,
  });
  // Keep last 1000 exchanges for learning
  if (conversations.length > 1000) conversations = conversations.slice(-1000);
  fs.writeFileSync(CONVO_FILE, JSON.stringify(conversations, null, 2));
}

loadData();

// ── Ollama proxy ─────────────────────────────────────────
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
const DEFAULT_MODEL = process.env.OLLAMA_MODEL || "llama3";

function buildSystemPrompt() {
  let sys = `You are JARVIS, an advanced AI assistant. You are helpful, precise, and professional.
Speak concisely. Format code in markdown code blocks.`;

  if (memory.userName) sys += `\nThe user's name is ${memory.userName}. Address them by name occasionally.`;

  if (memory.learned && memory.learned.length > 0) {
    const recent = memory.learned.slice(-10).map(f => `- ${f}`).join("\n");
    sys += `\nThings you have learned about this user:\n${recent}`;
  }

  if (Object.keys(memory.facts).length > 0) {
    const facts = Object.entries(memory.facts).map(([k, v]) => `- ${k}: ${v}`).join("\n");
    sys += `\nRemembered facts:\n${facts}`;
  }

  return sys;
}

function detectModel(message) {
  const m = message.toLowerCase();
  if (m.match(/code|script|write|program|function|debug|fix|python|lua|javascript|html|css|api|class|def |const |var /))
    return process.env.CODER_MODEL || "qwen2.5-coder";
  return DEFAULT_MODEL;
}

// Self-learning: extract facts from conversation
function learnFromConversation(userMsg, botReply) {
  const m = userMsg.toLowerCase();

  // Learn user's name
  const nameMatch = userMsg.match(/(?:my name is|call me|i am|i'm)\s+([A-Z][a-z]+)/i);
  if (nameMatch) {
    memory.userName = nameMatch[1];
  }

  // Learn facts the user states about themselves
  const factPatterns = [
    { regex: /i (?:work|am working) (?:at|for|with) (.+)/i, key: "works_at" },
    { regex: /i (?:live|am) in (.+)/i, key: "location" },
    { regex: /i (?:like|love|enjoy) (.+)/i, key: "likes" },
    { regex: /i (?:hate|dislike|don't like) (.+)/i, key: "dislikes" },
    { regex: /i am a (.+)/i, key: "role" },
    { regex: /i'm (?:a |an )?(.+)/i, key: "is" },
    { regex: /i (?:use|prefer) (.+)/i, key: "prefers" },
  ];

  for (const { regex, key } of factPatterns) {
    const match = userMsg.match(regex);
    if (match) {
      const value = match[1].trim().slice(0, 80);
      memory.facts[key] = value;
      if (!memory.learned.includes(`${key}: ${value}`))
        memory.learned.push(`${key}: ${value}`);
    }
  }

  saveMemory();
  saveConversation(userMsg, botReply);
}

// ── Routes ───────────────────────────────────────────────
app.get("/health", (req, res) => res.json({ status: "ok", model: DEFAULT_MODEL }));

app.get("/", (req, res) =>
  res.sendFile(path.join(sitePath, "index.html"))
);

app.post("/chat", async (req, res) => {
  const { message, history = [] } = req.body;
  if (!message) return res.status(400).json({ error: "Message required" });

  const model = detectModel(message);
  const systemPrompt = buildSystemPrompt();

  // Build messages array for Ollama
  const messages = [
    { role: "system", content: systemPrompt },
    ...history.slice(-10), // last 10 exchanges for context
    { role: "user", content: message },
  ];

  try {
    const fetch = require("node-fetch");
    const ollamaRes = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, messages, stream: false }),
      timeout: 120000,
    });

    if (!ollamaRes.ok) throw new Error(`Ollama HTTP ${ollamaRes.status}`);

    const data = await ollamaRes.json();
    const reply = data.message?.content || "I encountered an issue, sir.";

    learnFromConversation(message, reply);

    res.json({ reply, model });
  } catch (err) {
    console.error("Ollama error:", err.message);

    // Graceful fallback if Ollama is down
    res.json({
      reply: `Systems are temporarily limited, sir. Ollama may be offline. (${err.message})`,
      model: "fallback",
    });
  }
});

// Memory endpoints
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
app.listen(PORT, "0.0.0.0", () =>
  console.log(`🤖 JARVIS online → port ${PORT}`)
);
