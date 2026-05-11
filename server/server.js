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

// ============================================
// JARVIS: Self-Learning AI System
// ============================================

const DATA_DIR = path.join(__dirname, "../data");
const FACTS_FILE = path.join(DATA_DIR, "facts.txt");
const HISTORY_FILE = path.join(DATA_DIR, "chat_history.txt");

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

// Load knowledge base
let knowledgeBase = { facts: [], conversations: [] };

function loadKnowledge() {
  try {
    // Load facts
    if (fs.existsSync(FACTS_FILE)) {
      const factsContent = fs.readFileSync(FACTS_FILE, "utf-8");
      knowledgeBase.facts = factsContent.split("\n").filter(line => line.trim().length > 2);
    }
    
    // Load conversation history for learning
    if (fs.existsSync(HISTORY_FILE)) {
      const historyContent = fs.readFileSync(HISTORY_FILE, "utf-8");
      const lines = historyContent.split("\n").filter(line => line.includes("|"));
      knowledgeBase.conversations = lines.slice(-500); // Keep last 500
    }
    
    console.log(`Loaded ${knowledgeBase.facts.length} facts, ${knowledgeBase.conversations.length} past conversations`);
  } catch (e) {
    console.log("Knowledge loading:", e.message);
  }
}

// Save new knowledge
function saveKnowledge(fact) {
  try {
    if (fact && fact.length > 10 && !knowledgeBase.facts.some(f => f.includes(fact.slice(0, 30)))) {
      fs.appendFileSync(FACTS_FILE, fact + "\n");
      knowledgeBase.facts.push(fact);
    }
  } catch (e) {
    console.log("Save fact error:", e.message);
  }
}

// Log conversation for learning
function logConversation(userMsg, botMsg) {
  try {
    const logLine = `${new Date().toISOString()}|USER:${userMsg}|BOT:${botMsg}\n`;
    fs.appendFileSync(HISTORY_FILE, logLine);
  } catch (e) {
    console.log("Log error:", e.message);
  }
}

// Extract learnable facts from conversation
function learnFromConversation(userMsg, botMsg) {
  const importantWords = ["ai", "machine learning", "neural", "transformer", "python", "javascript", "html", "css", "api", "github", "git", "database", "server", "client", "http", "json"];
  
  // Learn any new factual statements
  if (botMsg.length > 20 && botMsg.length < 200) {
    const isQuestion = botMsg.includes("?");
    const hasInfo = importantWords.some(w => botMsg.toLowerCase().includes(w));
    if (!isQuestion && hasInfo) {
      // Clean up the response and save as a learnable fact
      const fact = botMsg.replace(/`/g, "").replace(/\n/g, " ").trim();
      saveKnowledge(fact);
    }
  }
}

// ============================================
// INTELLIGENT RESPONSE SYSTEM
// ============================================

// Keyword-to-fact responses
function getFactResponse(keyword) {
  const keywordLower = keyword.toLowerCase();
  
  // Search facts
  for (const fact of knowledgeBase.facts) {
    if (fact.toLowerCase().includes(keywordLower)) {
      return fact;
    }
  }
  
  // Search past conversations
  for (const conv of knowledgeBase.conversations) {
    if (conv.toLowerCase().includes(keywordLower)) {
      const parts = conv.split("|");
      if (parts[2] && parts[2].includes(keyword)) {
        return parts[2].replace("BOT:", "").trim();
      }
    }
  }
  
  return null;
}

// Intent detection
function detectIntent(message) {
  const m = message.toLowerCase();
  
  // Code generation
  if (m.match(/make|write|create|code for|generate|script/i) && 
      (m.includes("lua") || m.includes("python") || m.includes("javascript") || m.includes("html") || m.includes("api"))) {
    return "generate";
  }
  
  // Learning
  if (m.match(/what is|how does|how do|explain|teach me|learn about|what are|why does/i)) {
    return "learn";
  }
  
  // Debug help
  if (m.includes("bug") || m.includes("error") || m.includes("debug") || m.includes("fix") || m.includes("not working")) {
    return "debug";
  }
  
  // Greetings
  if (m.startsWith("hello") || m.startsWith("hi") || m.startsWith("hey") || m.match(/^good (morning|afternoon|evening)/i)) {
    return "greet";
  }
  
  // Identity
  if (m.includes("who are you") || m.includes("what are you") || m.includes("your name") || m.includes("who is")) {
    return "identity";
  }
  
  // Thanks/bye
  if (m.includes("thank") || m.includes("thanks") || m.includes("appreciate")) return "thanks";
  if (m.includes("bye") || m.includes("later") || m.includes("goodbye")) return "bye";
  
  // Help
  if (m === "help" || m.includes("what can you do")) return "help";
  
  // Default
  return "chat";
}

// Code generation
function generateCode(message) {
  const m = message.toLowerCase();
  
  if (m.includes("lua") || m.includes("fly")) {
    return `Here is a Roblox fly script:
\`\`\`lua
local player = game.Players.LocalPlayer
local char = player.Character
local hf = char:WaitForChild("HumanoidRootPart")
local bv = Instance.new("BodyVelocity")
bv.MaxForce = Vector3.new(4e5,4e5,4e5)
bv.Velocity = Vector3.new(0,50,0)
bv.Parent = hf
wait(3)
bv:Destroy()
\`\`\`
Press E to toggle fly!`;
  }
  
  if (m.includes("python") || m.includes("api")) {
    return `Python Flask API:
\`\`\`python
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello!"})

@app.route("/api/data", methods=["GET","POST"])  
def data():
    return jsonify({"data": request.json if request.method == "POST" else []})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
\`\`\``;
  }
  
  if (m.includes("javascript") || m.includes("js")) {
    return `JavaScript Express API:
\`\`\`javascript
const express = require("express");
const app = express();
app.use(express.json());

app.get("/api/hello", (req, res) => 
  res.json({ message: "Hello!" }));

app.listen(3000, () => console.log("Running on 3000"));
\`\`\``;
  }
  
  if (m.includes("html")) {
    return `Simple HTML:
\`\`\`html
<!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body>
  <h1>Hello World!</h1>
</body>
</html>
\`\`\``;
  }
  
  return "What type of code? I can generate Lua, Python, JavaScript, or HTML.";
}

// Main response generator - THE BRAIN
function getReply(message) {
  const intent = detectIntent(message);
  const m = message.toLowerCase();
  
  // GREETING
  if (intent === "greet") {
    const greetings = [
      "Hey! I'm Jarvis, your self-learning AI! What are you building?",
      "Hi! I learn from every conversation. What do you need?",
      "Hello! I'm getting smarter every day. What's on your mind?",
      "Hey there! I can code, explain things, or just chat. What do you want?",
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }
  
  // CODE GENERATION
  if (intent === "generate") {
    return generateCode(message);
  }
  
  // LEARN/EXPLAIN
  if (intent === "learn") {
    // Check for specific topics first
    const topics = {
      "python": "Python is a versatile programming language. Easy syntax, great for AI, web, data science. Libraries: NumPy, PyTorch, Flask, Django.",
      "javascript": "JavaScript runs the web! Used in browsers and servers (Node.js). Creates interactive websites. Uses async/await, has npm for packages.",
      "html": "HTML structures web pages with tags like <div>, <p>, <header>. CSS styles them, JavaScript adds interactivity.",
      "css": "CSS styles web pages - colors, fonts, layouts. Flexbox and Grid are powerful layouts.",
      "ai": "AI creates systems that learn from data. Machine learning trains models. Neural networks use layers. Transformers power modern AI like GPT!",
      "machine learning": "ML teaches computers from data instead of explicit programming. Types: supervised, unsupervised, reinforcement learning.",
      "neural network": "Neural networks are inspired by brains. Layers of 'neurons' learn patterns by adjusting weights during training.",
      "transformer": "Transformers use attention to understand context. They process all words at once - enabling GPT and modern AI!",
      "api": "APIs let programs communicate. REST uses HTTP methods: GET (read), POST (create), PUT (update), DELETE (remove).",
      "github": "GitHub hosts code. Use git add, commit, push, pull. Pull requests review code before merging.",
      "git": "Git tracks code changes. Commands: git add, commit, push, pull, merge, branch.",
      "database": "Databases store data. SQL uses tables (PostgreSQL, MySQL). NoSQL uses documents (MongoDB).",
    };
    
    for (const [topic, explanation] of Object.entries(topics)) {
      if (m.includes(topic)) return explanation;
    }
    
    // Check learned facts
    const fact = getFactResponse(message.split(" ")[1]);
    if (fact) return fact;
    
    return "What do you want to learn about? I know Python, JavaScript, HTML, CSS, AI, machine learning, APIs, GitHub, and more!";
  }
  
  // DEBUG
  if (intent === "debug") {
    return "I'd be happy to help debug! Could you share the code and the error message you're seeing?";
  }
  
  // IDENTITY
  if (intent === "identity") {
    return "I'm Jarvis, your self-learning AI! I learn from every conversation and get smarter over time. I can generate code, explain tech concepts, and help you build things. What do you need?";
  }
  
  // HELP
  if (intent === "help") {
    return "I can:\n- Generate code (Lua, Python, JavaScript, HTML)\n- Explain anything tech\n- Learn from our chats\n- Remember facts\n\nJust tell me what you need!";
  }
  
  // THANKS
  if (intent === "thanks") {
    return "You're welcome! I learn from every conversation. Anything else?";
  }
  
  // BYE
  if (intent === "bye") {
    return "See you later! I keep learning from our chats. Bye!";
  }
  
  // CHAT - search learned facts first!
  if (m.length > 3) {
    // Try to find relevant learned info
    const words = m.split(" ").filter(w => w.length > 3);
    for (const word of words.slice(0, 3)) {
      const fact = getFactResponse(word);
      if (fact && fact.length > 20) return fact;
    }
  }
  
  // Default conversation
  const chatResponses = [
    "Tell me more! What are you working on?",
    "I learn from every chat. What do you want to build?",
    "What kind of project are you making?",
    "I'm Jarvis - I get smarter from our chats! What do you need?",
    "Want to learn something or build something?",
  ];
  
  return chatResponses[Math.floor(Math.random() * chatResponses.length)];
}

// ============================================
// ROUTES
// ============================================

app.get("/", (req, res) => {
  res.sendFile(path.join(sitePath, "index.html"));
});

app.post("/chat", async (req, res) => {
  try {
    const { message, userId = "default" } = req.body;
    if (!message || !message.trim()) {
      return res.status(400).json({ error: "Message required" });
    }

    if (!chatHistory.has(userId)) {
      chatHistory.set(userId, []);
    }
    const history = chatHistory.get(userId);
    const cleanMessage = message.trim();
    history.push({ role: "user", text: cleanMessage });

    // Get smart response
    const reply = getReply(cleanMessage);
    
    // LEARN from conversation!
    learnFromConversation(cleanMessage, reply);
    logConversation(cleanMessage, reply);

    history.push({ role: "assistant", text: reply });
    res.json({ reply, history });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Oops! Something went wrong." });
  }
});

// Initialize knowledge on startup
loadKnowledge();

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🤖 JARVIS AI running on port ${PORT}`);
  console.log(`📚 Knowledge: ${knowledgeBase.facts.length} facts learned`);
});
