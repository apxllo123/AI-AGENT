const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

// ==============================
// JARVIS AI SYSTEM
// ==============================

let jarvisState = {
  name: "Jarvis",
  userName: null,
};

const MEMORY_FILE = path.join(__dirname, "../data", "jarvis_memory.json");

function loadMemory() {
  try {
    if (fs.existsSync(MEMORY_FILE)) {
      const data = JSON.parse(fs.readFileSync(MEMORY_FILE, "utf-8"));
      Object.assign(jarvisState, data);
    }
  } catch (e) {
    console.log("Memory:", e.message);
  }
}

function saveMemory() {
  try {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify(jarvisState, null, 2));
  } catch (e) {
    console.log("Save:", e.message);
  }
}

function detectIntent(message) {
  const m = message.toLowerCase();
  if (m.startsWith("hello") || m.startsWith("hi") || m.startsWith("hey")) return "greet";
  if (m.includes("who are you")) return "identity";
  if (m.includes("help")) return "help";
  if (m.includes("status")) return "status";
  if (m.includes("thank")) return "thanks";
  if (m.includes("bye")) return "bye";
  if (m.includes("my name")) return "personal";
  if (m.match(/make|write|create|code|script/)) return "code";
  if (m.match(/what is|how does|explain/)) return "learn";
  return "chat";
}

function generateCode(request) {
  const m = request.toLowerCase();
  if (m.includes("lua") || m.includes("fly")) {
    return "Lua fly script:\n\n```lua\nlocal bv = Instance.new('BodyVelocity')\nbv.Velocity = Vector3.new(0,50,0)\nbv.Parent = script.Parent\nwait(3)\nbv:Destroy()\n```\n\nE to toggle";
  }
  if (m.includes("python") || m.includes("api")) {
    return "Python Flask:\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home(): return 'Hello!'\n```";
  }
  if (m.includes("javascript") || m.includes("js")) {
    return "Express JS:\n\n```javascript\nconst express = require('express');\napp = express();\napp.get('/', (r,s) => s.send('Hi'));\n```";
  }
  if (m.includes("html")) {
    return "HTML:\n\n```html\n<h1>Hello</h1>\n```";
  }
  return "I do Lua, Python, JS, HTML";
}

const knowledge = {
  python: "Python: easy syntax, great for AI/web. Libraries: NumPy, PyTorch, Flask.",
  javascript: "JavaScript: runs web! Used in browsers and Node.js.",
  html: "HTML: structures web pages with tags.",
  ai: "AI: creates systems that learn. ML trains from data.",
  "machine learning": "ML: teaches computers from data. Types: supervised, unsupervised.",
  "neural network": "Neural networks: layers that learn patterns.",
  transformer: "Transformers: use attention. Power GPT, BERT!",
  github: "GitHub: hosts code. git add, commit, push, pull.",
  api: "APIs: let programs communicate. REST: GET/POST/PUT/DELETE.",
};

function getJarvisResponse(message, userId) {
  const intent = detectIntent(message);
  const m = message.toLowerCase();
  
  if (!chatHistory.has(userId)) chatHistory.set(userId, []);
  
  if (intent === "greet") {
    return ["Good to see you, sir.", "At your service.", "Ready. What's on?"][Math.floor(Math.random() * 3)];
  }
  
  if (intent === "identity") {
    let r = "I am Jarvis, your AI.";
    if (jarvisState.userName) r += " You are " + jarvisState.userName;
    return r;
  }
  
  if (intent === "status") {
    return jarvisState.userName ? "I know you, " + jarvisState.userName + "." : "Say my name is [name].";
  }
  
  if (intent === "help") return "I code, explain, remember.";
  
  if (intent === "code") return generateCode(message);
  
  if (intent === "learn") {
    for (const [k, v] of Object.entries(knowledge)) {
      if (m.includes(k)) return v;
    }
    return "I know Python, JS, AI, ML, more.";
  }
  
  if (intent === "personal") {
    const match = message.match(/my name is (\w+)/i);
    if (match) {
      jarvisState.userName = match[1];
      saveMemory();
      return "Got it, " + jarvisState.userName + "!";
    }
  }
  
  if (intent === "thanks") return "Welcome, sir.";
  if (intent === "bye") return "Later!";
  
  return "Tell me more!";
}

app.get("/", (req, res) => res.sendFile(path.join(sitePath, "index.html")));

app.post("/chat", (req, res) => {
  const { message, userId = "default" } = req.body;
  if (!message) return res.status(400).json({error: "Message required"});

  if (!chatHistory.has(userId)) chatHistory.set(userId, []);
  const history = chatHistory.get(userId);
  history.push({role: "user", text: message});

  const reply = getJarvisResponse(message, userId);
  history.push({role: "assistant", text: reply});
  res.json({reply, history});
});

loadMemory();
const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => console.log("JARVIS on " + PORT));
