const express = require("express");
const cors = require("cors");
const path = require("path");
const http = require("http");

const app = express();
app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

// Try to connect to local Ollama
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
let useOllama = false;

// Check if Ollama is available
async function checkOllama() {
  try {
    const response = await fetch(OLLAMA_URL + "/api/tags", { 
      method: "POST",
      signal: { signal: false }
    });
    useOllama = response.ok;
    console.log("Ollama:", useOllama ? "Connected" : "Not available");
  } catch (e) {
    useOllama = false;
    console.log("Ollama: Not available");
  }
}

checkOllama();

// Jarvis personality
const KNOWLEDGE = {
  python: "Python: versatile language. Easy syntax, great for AI, web, data science.",
  javascript: "JavaScript: runs the web! In browsers and Node.js.",
  html: "HTML: structures web pages.",
  ai: "AI = Artificial Intelligence. Creates systems that learn.",
  "machine learning": "ML teaches computers from data.",
  "neural network": "Neural networks: layers that learn patterns.",
  transformer: "Transformers: use attention. Power GPT, BERT!",
  github: "GitHub: hosts code. Use git add, commit, push, pull.",
  api: "APIs: let programs communicate. REST has GET, POST, PUT, DELETE.",
};

function detectIntent(message) {
  const m = message.toLowerCase();
  if (m.startsWith("hello")) return "greet";
  if (m.includes("who are you")) return "identity";
  if (m.includes("help")) return "help";
  if (m.includes("status")) return "status";
  if (m.includes("thank")) return "thanks";
  if (m.includes("my name")) return "personal";
  if (m.match(/make|write|code|script/)) return "code";
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
  return "What type? Lua, Python, JS, HTML?";
}

function getReply(message, userId) {
  const intent = detectIntent(message);
  const m = message.toLowerCase();
  
  if (intent === "greet") {
    return ["Good to see you, sir.", "At your service.", "Ready. What's on?"][Math.floor(Math.random() * 3)];
  }
  if (intent === "identity") return "I am JARVIS, your AI. I can code, explain, remember.";
  if (intent === "status") return useOllama ? "Ollama connected. Full AI active." : "Running in limited mode.";
  if (intent === "help") return "I can: code, explain, remember your name.";
  if (intent === "code") return generateCode(message);
  if (intent === "learn") {
    for (const [k, v] of Object.entries(KNOWLEDGE)) {
      if (m.includes(k)) return v;
    }
    return "I know Python, JS, AI, ML, more.";
  }
  if (intent === "personal") {
    const match = message.match(/my name is (\w+)/i);
    if (match) return `Got it, ${match[1]}!`;
  }
  if (intent === "thanks") return "Welcome, sir.";
  
  return "Tell me more! What do you need?";
}

app.get("/", (req, res) => res.sendFile(path.join(sitePath, "index.html")));

app.post("/chat", async (req, res) => {
  const { message, userId = "default" } = req.body;
  if (!message) return res.status(400).json({error: "Message required"});
  if (!chatHistory.has(userId)) chatHistory.set(userId, []);
  const history = chatHistory.get(userId);
  history.push({role: "user", text: message});

  let reply;
  
  // Try Ollama first if available
  if (useOllama) {
    try {
      const response = await fetch(OLLAMA_URL + "/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          model: "llama3",
          messages: [
            {role: "system", content: "You are JARVIS, a helpful AI."},
            ...history.slice(-4),
            {role: "user", content: message}
          ],
          stream: false
        }),
        signal: AbortSignal.timeout(60000)
      });
      const data = await response.json();
      reply = data.message?.content;
    } catch (e) {
      console.log("Ollama error:", e.message);
      useOllama = false;
    }
  }
  
  // Fallback to local brain
  if (!reply) {
    reply = getReply(message, userId);
  }
  
  history.push({role: "assistant", text: reply});
  res.json({reply, history, ollama: useOllama});
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => console.log("JARVIS on " + PORT));
