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

// Load memory
const MEMORY_FILE = path.join(__dirname, "../data", "jarvis_memory.json");
let jarvisMemory = { userName: null, learned: [] };

try {
  if (fs.existsSync(MEMORY_FILE)) {
    jarvisMemory = JSON.parse(fs.readFileSync(MEMORY_FILE, "utf-8"));
  }
} catch (e) {}

// Extended knowledge base
const KNOWLEDGE = {
  // Programming
  python: "Python is versatile. Great for AI, web, data science. Libraries: NumPy, PyTorch, Flask, Django. Syntax is clean and readable. Use indentation for blocks.",
  javascript: "JavaScript runs the web! Used in browsers and servers (Node.js). Key: async/await, closures, prototypes. Use npm for packages.",
  html: "HTML structures web pages with tags like <div>, <p>, <header>, <footer>. CSS styles them, JavaScript adds interactivity.",
  css: "CSS styles web pages - colors, fonts, layouts. Flexbox and Grid are powerful for layouts. Use class selectors.",
  java: "Java is a compiled language. Object-oriented. Write once run anywhere. Used in Android apps and enterprise.",
  csharp: "C# is Microsoft's language. Used for Windows apps, games (Unity), .NET development.",
  cpp: "C++ is powerful and fast. Low-level memory control. Used in games, systems, performance-critical code.",
  rust: "Rust is safe and fast. Memory safe without garbage collection. Used for systems programming.",
  go: "Go is simple and fast. Made by Google. Good for APIs, microservices, CLI tools.",
  
  // Web/DevOps
  api: "APIs let programs talk. REST uses HTTP methods: GET (read), POST (create), PUT (update), DELETE (remove). Returns JSON.",
  http: "HTTP is how browsers talk to servers. Methods: GET, POST, PUT, DELETE. Status codes: 200 (OK), 404 (Not Found), 500 (Error).",
  json: "JSON is data format. Key-value pairs. Used in APIs. {\"name\": \"value\"}. Easy for programs to read.",
  github: "GitHub hosts code. Use: git add, commit -m 'message', push, pull. Pull requests for code review.",
  git: "Git tracks code changes. Commands: init, add, commit, push, pull, branch, merge. Distributed version control.",
  docker: "Docker packages apps with dependencies. Images are templates, containers are running instances. Use Dockerfile.",
  kubernetes: "Kubernetes manages containers at scale. Handles deployment, scaling, load balancing. K8s.",
  
  // AI/ML
  ai: "AI = Artificial Intelligence. Creates systems that learn. Machine learning trains from data. Deep learning uses neural networks.",
  "machine learning": "ML teaches computers from data, not explicit programming. Types: supervised (labeled data), unsupervised (patterns), reinforcement (rewards).",
  "neural network": "Neural networks inspired by brains. Layers of 'neurons' learn patterns by adjusting weights during training.",
  transformer: "Transformers use 'attention' to understand context. Process all words at once. Powers GPT, BERT, modern AI!",
  gpt: "GPT is Generative Pre-trained Transformer. Made by OpenAI. Large language model trained on internet text.",
  chatgpt: "ChatGPT is OpenAI's chatbot. Uses GPT-4. Great for conversation, coding, writing.",
  llama: "Llama is Meta's open source AI model. Runs locally! Smaller than GPT but free.",
  ollama: "Ollama runs AI models locally on your Mac. Download models: llama3, mistral, codellama.",
  
  // Concepts
  database: "Databases store data. SQL: tables, rows, columns (PostgreSQL, MySQL). NoSQL: documents (MongoDB), key-value (Redis).",
  sql: "SQL queries databases. SELECT * FROM table WHERE condition. INSERT, UPDATE, DELETE. Joins combine tables.",
  server: "Server provides services. Listens for requests. Express.js, Flask, FastAPI for web servers.",
  client: "Client requests services. Browsers, mobile apps, other servers make requests.",
  
  // Roblox/Lua
  lua: "Lua is scripting for games. Roblox uses Lua. Lightweight, easy to learn.",
  roblox: "Roblox is a game platform. Uses Lua for scripting. Create games, tools, UI with scripts.",
  
  // General
  linux: "Linux is an operating system. Open source. Ubuntu, Debian, CentOS are popular distros. Uses terminal.",
  ubuntu: "Ubuntu is a popular Linux. Easy to use. apt for packages. sudo for admin.",
  terminal: "Terminal is command line. Type commands. bash is the shell. cd, ls, grep, cat are common.",
  vscode: "VSCode is a code editor. Free from Microsoft. Extensions for languages. IntelliSense, debugging.",
};

// Code templates
const CODE_TEMPLATES = {
  lua_fly: `local player = game.Players.LocalPlayer
local char = player.Character
local root = char:WaitForChild("HumanoidRootPart")

local flying = false
local speed = 50

local bv = Instance.new("BodyVelocity")
bv.MaxForce = Vector3.new(4e5, 4e5, 4e5)
bv.Velocity = Vector3.new(0, speed, 0)
bv.Parent = root

-- Toggle with E key
game:GetService("UserInputService").InputBegan:Connect(function(input)
  if input.KeyCode == Enum.KeyCode.E then
    if flying then
      bv.Velocity = Vector3.new(0, 0, 0)
      flying = false
    else
      bv.Velocity = Vector3.new(0, speed, 0)
      flying = true
    end
  end
end)`,

  python_api: `from flask import Flask, jsonify, request
  
app = Flask(__name__)

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello, sir!"})

@app.route("/api/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    return jsonify({"reply": f"You said: {user_msg}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)`,

  javascript_api: `const express = require("express");
const app = express();

app.use(express.json());

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello!" });
});

app.post("/api/chat", (req, res) => {
  const { message } = req.body;
  res.json({ reply: "You said: " + message });
});

app.listen(3000, () => console.log("Server on 3000"));`,

  html_basic: `<!DOCTYPE html>
<html>
<head>
  <title>My Page</title>
</head>
<body>
  <h1>Hello World!</h1>
  <p>Powered by JARVIS AI</p>
</body>
</html>`,

  python_bot: `import random

responses = {
  "hello": ["Hi!", "Hello!", "Hey there!"],
  "how are you": ["I'm doing great!", "Operational as always."],
  "default": ["Tell me more!", "What do you need?"]
}

def get_response(user_input):
  for key, responses in responses.items():
    if key in user_input.lower():
      return random.choice(responses)
  return random.choice(responses["default"])`,
};

function detectIntent(message) {
  const m = message.toLowerCase();
  
  if (m.startsWith("hello") || m.startsWith("hi") || m.startsWith("hey")) return "greet";
  if (m.includes("who are you") || m.includes("what are you")) return "identity";
  if (m.includes("how are you") || m.includes("status")) return "status";
  if (m.includes("help") || m === "help") return "help";
  if (m.includes("thank")) return "thanks";
  if (m.includes("bye")) return "bye";
  if (m.includes("my name") || m.includes("call me")) return "personal";
  if (m.includes("remember")) return "remember";
  if (m.match(/make|write|create|code|generate|script|program|build/)) return "code";
  if (m.match(/what is|how does|explain|tell me about|what are|why|/)) return "learn";
  if (m.match(/search|find|look up|google/)) return "search";
  if (m.includes("?")) return "learn";
  
  return "chat";
}

function generateCode(type) {
  if (type.includes("fly")) return "```lua\n" + CODE_TEMPLATES.lua_fly + "\n```\n\nE key toggle!";
  if (type.includes("python") || type.includes("flask") || type.includes("api")) return "```python\n" + CODE_TEMPLATES.python_api + "\n```";
  if (type.includes("javascript") || type.includes("express") || type.includes("js ")) return "```javascript\n" + CODE_TEMPLATES.javascript_api + "\n```";
  if (type.includes("html") || type.includes("website")) return CODE_TEMPLATES.html_basic;
  if (type.includes("bot")) return "```python\n" + CODE_TEMPLATES.python_bot + "\n```";
  if (type.includes("react")) return "```jsx\nfunction App() {\n  return <h1>Hello!</h1>;\n}\n```";
  if (type.includes("css")) return "```css\nbody {\n  font-family: sans-serif;\n  background: #1a1a2e;\n  color: white;\n}\n```";
  
  return "What type of code? I can do Python, JavaScript, Lua, HTML, CSS.";
}

function getReply(message, userId) {
  const intent = detectIntent(message);
  const m = message.toLowerCase();
  
  if (intent === "greet") {
    const greetings = [
      "Good to see you, sir. What are we building?",
      "At your service. What do you need?",
      "Systems online. How may I assist?",
      "Good afternoon. Ready to work.",
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }
  
  if (intent === "identity") {
    let r = "I am JARVIS, your AI assistant. ";
    r += "I can write code, explain technology, help with projects. ";
    if (jarvisMemory.userName) r += "I know you as " + jarvisMemory.userName + ". ";
    return r;
  }
  
  if (intent === "status") {
    const learned = jarvisMemory.learned?.length || 0;
    return "All systems operational. " + 
      (jarvisMemory.userName ? `I recognize you, ${jarvisMemory.userName}. ` : "I don't know your name yet. ") +
      `I've learned ${learned} things. What do you need?`;
  }
  
  if (intent === "help") {
    return `I can help with:\n\n` +
      `📝 **Code** - "write me a lua fly script", "create python api"\n` +
      `📚 **Learn** - "what is python", "how does neural network work"\n` +
      `💾 **Remember** - "my name is [name]"\n` +
      `💬 **Chat** - Just talk!\n\n` +
      `Try asking about Python, JavaScript, AI, GitHub, databases, or anything tech!`;
  }
  
  if (intent === "code") return generateCode(m);
  
  if (intent === "learn") {
    // Search for keywords in message
    for (const [key, value] of Object.entries(KNOWLEDGE)) {
      if (m.includes(key)) return value;
    }
    
    // Check learned facts
    if (jarvisMemory.learned?.length > 0) {
      for (const fact of jarvisMemory.learned) {
        if (m.includes(fact.word)) return fact.answer;
      }
    }
    
    return "I know about: Python, JavaScript, HTML, CSS, AI, machine learning, neural networks, transformers, GitHub, Git, APIs, databases, Docker, Kubernetes, React, Node, Linux, and more. What interests you?";
  }
  
  if (intent === "personal") {
    const nameMatch = message.match(/my name is (\w+)/i) || message.match(/call me (\w+)/i);
    if (nameMatch) {
      jarvisMemory.userName = nameMatch[1];
      fs.writeFileSync(MEMORY_FILE, JSON.stringify(jarvisMemory, null, 2));
      return `Got it, ${jarvisMemory.userName}! How can I help you?`;
    }
    return "What would you like me to remember?";
  }
  
  if (intent === "search") {
    return "I'd search for that but web search requires more setup. Try asking a specific question - I know about lots of tech topics!";
  }
  
  if (intent === "thanks") {
    return "You're welcome, sir. Always at your service.";
  }
  
  if (intent === "bye") {
    return "Good bye! Talk soon.";
  }
  
  // Default - try to be helpful
  const chatResponses = [
    "Tell me more! What are you working on?",
    "I can help with coding, explain concepts, or just chat.",
    "What do you need? Code, explanations, or something else?",
    "Ask me about Python, JavaScript, AI, or anything tech!",
  ];
  return chatResponses[Math.floor(Math.random() * chatResponses.length)];
}

app.get("/", (req, res) => res.sendFile(path.join(sitePath, "index.html")));

app.post("/chat", (req, res) => {
  const { message, userId = "default" } = req.body;
  if (!message) return res.status(400).json({error: "Message required"});
  
  if (!chatHistory.has(userId)) chatHistory.set(userId, []);
  const history = chatHistory.get(userId);
  history.push({role: "user", text: message});
  
  const reply = getReply(message, userId);
  history.push({role: "assistant", text: reply});
  
  res.json({reply, history});
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => console.log("🤖 JARVIS on " + PORT));
