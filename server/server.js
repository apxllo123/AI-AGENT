const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

// ============================================
// SMART CONVERSATIONAL AI
// ============================================

// Intent recognition - what does the user want?
function detectIntent(message) {
  const m = message.toLowerCase();
  
  // Code generation requests
  if (m.match(/make\s+(me\s+)?(a\s+)?(lua|python|javascript|html|css|sql|api|script)/i) ||
      m.match(/write\s+(me\s+)?(a\s+)?(lua|python|javascript|html|css|sql|api|script)/i) ||
      m.match(/create\s+(me\s+)?(a\s+)?(lua|python|javascript|html|css|sql|api|script)/i) ||
      m.includes("code for") || m.includes("write code")) {
    return "generate";
  }
  
  // Debug/help requests  
  if (m.includes("debug") || m.includes("fix") || m.includes("error") || 
      m.includes("not working") || m.includes("bug")) {
    return "debug";
  }
  
  // Learning requests
  if (m.match(/how\s+(do|does|to|can)/i) || m.match(/what\s+(is|are|does)/i) ||
      m.match(/why\s+(does|is|can)/i) || m.match(/explain/i) || m.includes("learn about")) {
    return "learn";
  }
  
  // Greetings
  if (m.startsWith("hello") || m.startsWith("hi") || m.startsWith("hey") || 
      m.startsWith("howdy") || m.startsWith("greetings") || m.startsWith("good")) {
    return "greet";
  }
  
  // Thanks
  if (m.includes("thank") || m.includes("thanks") || m.includes("appreciate")) {
    return "thanks";
  }
  
  // Goodbye
  if (m.includes("bye") || m.includes("goodbye") || m.includes("see you") || m.includes("later")) {
    return "bye";
  }
  
  // Help request
  if (m.match(/^help$/i) || m.includes("what can you do")) {
    return "help";
  }
  
  // Who are you
  if (m.includes("who are you") || m.includes("what are you") || m.includes("your name")) {
    return "identity";
  }
  
  // Default to conversation
  return "chat";
}

// Code generators for common requests
function generateCode(language, request) {
  const templates = {
    lua: {
      fly: `-- Fly script for Roblox games
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()

local flying = false
local speed = 50

local function startFly()
    flying = true
    local velocity = Instance.new("BodyVelocity")
    velocity.MaxForce = Vector3.new(400000, 400000, 400000)
    velocity.Velocity = Vector3.new(0, speed, 0)
    velocity.Parent = character.HumanoidRootPart
end

local function stopFly()
    flying = false
    if character.HumanoidRootPart:FindFirstChild("BodyVelocity") then
        character.HumanoidRootPart.BodyVelocity:Destroy()
    end
end

-- Toggle fly with E key
game:GetService("UserInputService").InputBegan:Connect(function(input)
    if input.KeyCode == Enum.KeyCode.E then
        if flying then stopFly() else startFly() end
    end
end)`,
      },
    python: {
      api: `# Simple Flask API
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello, World!"})

@app.route("/api/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        return jsonify({"received": request.json})
    return jsonify({"data": []})

if __name__ == "__main__":
    app.run(debug=True, port=5000)`,
      },
      bot: `# Discord Bot
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run("YOUR_TOKEN")`,
      },
    },
    javascript: {
      api: `// Express API Server
const express = require("express");
const app = express();
app.use(express.json());

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello, World!" });
});

app.post("/api/data", (req, res) => {
  res.json({ received: req.body });
});

app.listen(3000, () => console.log("Server running on port 3000"));`,
      website: `// Simple Website
<!DOCTYPE html>
<html>
<head>
  <title>My Website</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
  </style>
</head>
<body>
  <h1>Welcome!</h1>
  <p>This is my website.</p>
  <script>
    console.log("Hello from JavaScript!");
  </script>
</body>
</html>`,
      },
    },
    html: {
      basic: `<!DOCTYPE html>
<html>
<head>
  <title>My Page</title>
</head>
<body>
  <h1>Hello World!</h1>
</body>
</html>`,
    },
  };
  
  // Check for specific requests
  if (language === "lua") {
    if (request.includes("fly")) return templates.lua.fly;
    return templates.lua.api;
  }
  if (language === "python") {
    if (request.includes("api")) return templates.python.api;
    if (request.includes("bot")) return templates.python.bot;
    return templates.python.api;
  }
  if (language === "javascript" || language === "js") {
    if (request.includes("api")) return templates.javascript.api;
    if (request.includes("website") || request.includes("page")) return templates.javascript.website;
    return templates.javascript.api;
  }
  if (language === "html") return templates.html.basic;
  
  return "I can generate Lua, Python, JavaScript, and HTML code. What do you need?";
}

// Main response generator
function getReply(message) {
  const intent = detectIntent(message);
  const m = message.toLowerCase();
  
  // Greeting
  if (intent === "greet") {
    const greetings = [
      "Hey! What are you working on?",
      "Hi there! Want to code something?",
      "Hello! I can help you build things. What do you want to make?",
      "Hey! Need help with code, or want to learn something?",
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }
  
  // Code generation
  if (intent === "generate") {
    // Detect language
    let lang = "javascript";
    if (m.includes("lua")) lang = "lua";
    else if (m.includes("python")) lang = "python";
    else if (m.includes("html")) lang = "html";
    else if (m.includes("js")) lang = "javascript";
    
    const code = generateCode(lang, m);
    return `Here's ${lang} code for that:\n\n\`\`\`${lang === "lua" ? "lua" : lang === "js" ? "javascript" : lang}\n${code}\n\`\`\`\n\nWant me to explain how it works?`;
  }
  
  // Learning/explanation
  if (intent === "learn") {
    const explanations = {
      "python": "Python is a versatile programming language. Key features: easy syntax, dynamically typed, great libraries (NumPy, PyTorch, Flask). Used for AI, web, data science.",
      "javascript": "JavaScript runs the web! In browsers and servers (Node.js). Creates interactive websites, APIs, mobile apps. Uses async/await, promises, and has npm for packages.",
      "html": "HTML structures web pages. Uses tags like <div>, <p>, <a>. CSS styles it, JavaScript adds interactivity.",
      "css": "CSS styles web pages - colors, fonts, layouts. Flexbox and Grid are powerful layout systems.",
      "api": "APIs (Application Programming Interfaces) let programs talk. REST uses HTTP methods: GET (read), POST (create), PUT (update), DELETE (remove).",
      "github": "GitHub hosts code. Use git add, commit, push, pull. Pull requests review code before merging.",
      "git": "Git tracks code changes. Commands: git init, git add, git commit -m 'message', git push, git pull.",
      "ai": "AI creates systems that learn. Machine learning trains on data. Neural networks use layers. Transformers power modern AI like GPT.",
      "machine learning": "ML teaches computers from data. Types: supervised (labeled data), unsupervised (find patterns), reinforcement (learning from rewards).",
      "neural": "Neural networks are inspired by brains. Layers of 'neurons' learn patterns. Trained by adjusting weights to minimize loss.",
      "transformer": "Transformers use 'attention' to understand context. They process all words at once, enabling GPT and modern AI.",
    };
    
    for (const [topic, explanation] of Object.entries(explanations)) {
      if (m.includes(topic)) return explanation;
    }
    
    return "What specifically do you want to learn about? I can explain Python, JavaScript, HTML, CSS, APIs, GitHub, Git, AI, machine learning, neural networks, transformers, and more!";
  }
  
  // Identity
  if (intent === "identity") {
    return "I'm AI-AGENT, your AI assistant! I can help you code, explain tech concepts, debug issues, and answer questions. What do you need?";
  }
  
  // Help
  if (intent === "help") {
    return "I can help you with:\n- Writing code (Lua, Python, JavaScript, HTML)\n- Explaining tech concepts\n- Debugging issues\n- Learning programming\n\nJust tell me what you need!";
  }
  
  // Thanks
  if (intent === "thanks") {
    return "You're welcome! Anything else you need?";
  }
  
  // Goodbye
  if (intent === "bye") {
    return "See you later! Happy coding!";
  }
  
  // Debug help
  if (intent === "debug") {
    return "I'd be happy to help debug! Can you share the code and what error you're seeing?";
  }
  
  // Chat - try to be helpful
  const chatResponses = [
    "Tell me more about what you're building!",
    "What kind of project are you working on?",
    "I can generate code, explain concepts, or help debug. What do you need?",
    "Want to build something? Tell me what!",
    "What are you trying to accomplish?",
  ];
  
  return chatResponses[Math.floor(Math.random() * chatResponses.length)];
}

// ============================================
// Express Routes
// ============================================

app.get("/", (req, res) => {
  res.sendFile(path.join(sitePath, "index.html"));
});

app.post("/chat", async (req, res) => {
  try {
    const { message, userId = "default" } = req.body;
    if (!message || !message.trim()) {
      return res.status(400).json({ error: "Message is required" });
    }

    if (!chatHistory.has(userId)) {
      chatHistory.set(userId, []);
    }
    const history = chatHistory.get(userId);
    const cleanMessage = message.trim();
    history.push({ role: "user", text: cleanMessage });

    const reply = getReply(cleanMessage);

    history.push({ role: "assistant", text: reply });
    res.json({ reply, history });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Oops! Something went wrong." });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`AI-AGENT running on port ${PORT}`);
});
