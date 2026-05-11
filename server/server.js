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
// SMART AI - Picks coherent sentences from training data
// ============================================

// Complete coherent sentences to pick from
const RESPONSE_POOL = [
  // Greetings
  "Hello! How are you doing today?",
  "Hey there! Good to see you!",
  "Hi! What would you like to discuss?",
  "Welcome! How can I help you today?",
  "Good to see you! What is on your mind?",
  // AI & Tech
  "AI creates systems that can learn from data. Machine learning is a subset of ai.",
  "Neural networks learn from data. They are inspired by biological brains.",
  "Transformers use attention to understand context. They revolutionized NLP!",
  "Python is great for AI and data science. It has powerful libraries.",
  "JavaScript powers the web. It runs in browsers and servers.",
  "GitHub hosts code repositories. Git tracks all your code changes.",
  "APIs connect applications. REST is a popular style.",
  "JSON is a popular data format. It is easy to read and parse.",
  "HTML creates web page structure. CSS makes it beautiful.",
  "Functions organize code into reusable parts.",
  "Variables store information for later use.",
  "Loops repeat code many times.",
  "Conditions make decisions in code.",
  "Classes define new types of objects.",
  "Inheritance reuses code in classes.",
  "Databases store organized information.",
  "Cloud computing is very convenient.",
  "Servers listen for requests and respond.",
  "Testing makes code reliable.",
  "Bugs are errors in code that need fixing.",
  "Debugging finds and fixes bugs.",
  "Console logs help debug applications.",
  // Encouragement
  "That is a great question! Keep asking questions.",
  "Interesting perspective! Tell me more.",
  "I love that curiosity! Ask me anything.",
  "Great way to think about it! What else?",
  // Fallbacks
  "Tell me more about what you are working on.",
  "I am here to help! What would you like to know?",
  "Good question! Here is what I know...",
  "Let me think about that. What specifically?",
];

// Keyword-specific responses for accuracy
const KEYWORD_RESPONSES = {
  python: "Python is a versatile programming language great for AI, web development, data science, and automation. It has libraries like NumPy, PyTorch, Flask, and Django.",
  javascript: "JavaScript powers the web! It is used for interactive websites, web apps, mobile apps, and servers with Node.js.",
  html: "HTML (HyperText Markup Language) provides the structure of web pages using semantic tags like <header>, <main>, <article>.",
  css: "CSS (Cascading Style Sheets) styles web pages with colors, layouts, fonts, animations using Flexbox and Grid.",
  ai: "AI (Artificial Intelligence) creates systems that can learn, reason, and make decisions. Machine learning learns from data.",
  "machine learning": "Machine learning teaches computers to learn from data rather than explicit programming. Types include supervised, unsupervised, and reinforcement learning.",
  neural: "Neural networks are inspired by biological brains. They have layers of nodes that learn patterns through training.",
  transformer: "Transformers use attention mechanisms to understand context. They enabled GPT, BERT, and modern language models!",
  gpt: "GPT (Generative Pre-trained Transformer) is OpenAIs large language model that generates human-like text.",
  github: "GitHub hosts code repositories and enables collaboration through pull requests, issues, and code review.",
  git: "Git tracks code changes. Key commands: git add, git commit, git push, git pull, git merge.",
  api: "APIs (Application Programming Interfaces) let applications communicate. REST uses GET, POST, PUT, DELETE.",
  http: "HTTP is the web protocol. GET retrieves data, POST creates data, PUT updates, DELETE removes.",
  server: "Servers provide services to clients. They listen on ports and respond to requests.",
  database: "Databases store organized data. SQL databases use tables. NoSQL databases use documents.",
  cloud: "Cloud computing provides on-demand resources. AWS, GCP, and Azure offer great services.",
  bug: "Bugs are errors in code! Use console.log, debuggers, and error messages to find and fix them.",
  error: "Error messages tell you what went wrong! Read them carefully - they indicate the file and line number.",
  function: "Functions organize code into reusable blocks. They accept inputs and can return outputs.",
  class: "Classes define blueprints for creating objects with specific properties and methods.",
  variable: "Variables store data values that can change during execution. Use descriptive names.",
  loop: "Loops repeat code. For-loops iterate a known number of times. While-loops repeat until a condition changes.",
  array: "Arrays hold ordered lists of items. Access by index starting at 0.",
  learn: "Learning takes practice! Start with small projects, make mistakes, and build every day.",
  help: "I am here to help! Ask about programming, AI, web development, or any tech topic.",
  who: "I am AI-AGENT, your AI assistant!",
  name: "I am AI-AGENT, your personal AI assistant built with custom AI!",
};

function getReply(message) {
  const m = message.toLowerCase();
  
  // Check for greetings FIRST to avoid substring bugs
  if (m.startsWith("hello") || m.startsWith("hi") || m.startsWith("hey") || 
      m.startsWith("howdy") || m.startsWith("greetings")) {
    return RESPONSE_POOL[Math.floor(Math.random() * 5)]; // Return greeting responses
  }
  
  // Check keywords for accurate technical info
  for (const [keyword, response] of Object.entries(KEYWORD_RESPONSES)) {
    // Only match whole words to avoid substring matching
    const wordRegex = new RegExp("\\b" + keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "\\b");
    if (wordRegex.test(m)) return response;
  }
  
  // Pick a random coherent response for general chat
  return RESPONSE_POOL[Math.floor(Math.random() * RESPONSE_POOL.length)];
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
    res.status(500).json({ error: "Oops, something went wrong!" });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`AI-AGENT server running on port ${PORT}`);
});
