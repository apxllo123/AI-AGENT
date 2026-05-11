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

// OpenAI API Key
const OPENAI_API_KEY = "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";

const MODEL = "gpt-4o-mini";

// Memory
const MEMORY_FILE = path.join(__dirname, "../data", "jarvis_memory.json");
let jarvisMemory = { userName: null, learned: [] };

try {
  if (fs.existsSync(MEMORY_FILE)) {
    jarvisMemory = JSON.parse(fs.readFileSync(MEMORY_FILE, "utf-8"));
  }
} catch (e) {}

// Quick local knowledge (fallback)
const KNOWLEDGE = {
  python: "Python: versatile language. Easy syntax, great for AI, web, data science.",
  javascript: "JavaScript: runs the web!",
  ai: "AI = Artificial Intelligence",
  "machine learning": "ML teaches computers from data",
};

async function chatWithGPT(message, history) {
  const messages = [
    { role: "system", content: "You are JARVIS, a helpful AI assistant like Iron Man's JARVIS. Be concise, professional, helpful. You can write code in many languages." }
  ];
  
  // Add recent history
  for (const msg of history.slice(-8)) {
    messages.push(msg);
  }
  messages.push({ role: "user", content: message });

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + OPENAI_API_KEY
      },
      body: JSON.stringify({
        model: MODEL,
        messages: messages,
        max_tokens: 500
      })
    });

    const data = await response.json();
    return data.choices?.[0]?.message?.content || null;
  } catch (e) {
    console.log("GPT Error:", e.message);
    return null;
  }
}

function detectIntent(message) {
  const m = message.toLowerCase();
  if (m.startsWith("hello")) return "greet";
  if (m.includes("who are you")) return "identity";
  if (m.includes("help")) return "help";
  if (m.includes("thank")) return "thanks";
  if (m.includes("my name")) return "personal";
  return "chat";
}

function getLocalReply(message) {
  const m = message.toLowerCase();
  const intent = detectIntent(message);
  
  if (intent === "greet") {
    return ["Good to see you, sir.", "At your service.", "Systems online."][Math.floor(Math.random() * 3)];
  }
  if (intent === "identity") {
    return "I am JARVIS with GPT-4 intelligence!";
  }
  if (intent === "help") {
    return "I can help with anything! Code, explanations, conversation. Just ask!";
  }
  if (intent === "personal") {
    const match = message.match(/my name is (\w+)/i);
    if (match) {
      jarvisMemory.userName = match[1];
      fs.writeFileSync(MEMORY_FILE, JSON.stringify(jarvisMemory));
      return `Got it, ${jarvisMemory.userName}!`;
    }
  }
  if (intent === "thanks") return "You're welcome!";
  
  return "Let me think...";
}

app.get("/", (req, res) => res.sendFile(path.join(sitePath, "index.html")));

app.post("/chat", async (req, res) => {
  const { message, userId = "default" } = req.body;
  if (!message) return res.status(400).json({error: "Message required"});
  
  if (!chatHistory.has(userId)) chatHistory.set(userId, []);
  const history = chatHistory.get(userId);
  history.push({role: "user", content: message});

  // Try GPT-4 first
  let reply = await chatWithGPT(message, history);
  
  // Fallback to local
  if (!reply) {
    reply = getLocalReply(message);
  }

  history.push({role: "assistant", content: reply});
  res.json({reply, history});
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => console.log("🤖 JARVIS with GPT-4 on port " + PORT));
