const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

const FLASK_URL = process.env.FLASK_URL || "http://127.0.0.1:8080";

// Extensive keyword responses for programming/tech topics
const KEYWORD_RESPONSES = {
  python: "Python is a versatile programming language great for AI, web development, and data science. It has libraries like NumPy, PyTorch, Flask, Django, and pandas.",
  javascript: "JavaScript powers the web! It's used for interactive websites, web apps, and servers with Node.js. It runs in browsers and can build full-stack apps.",
  html: "HTML provides semantic structure for web pages using tags like <div>, <span>, <p>, <header>, <footer> to organize content.",
  css: "CSS styles web pages - colors, layouts, fonts, animations. Use selectors to target elements, Flexbox and Grid for layouts.",
  programming: "Programming is instructing computers through code. It uses variables, functions, loops, and conditions to express logic.",
  code: "Code is written in programming languages that computers execute. Good code is clean, well-organized, and documented.",
  learn: "Learning to code takes practice. Start with basics, build projects, and don't fear making mistakes - they're learning opportunities!",
  ai: "AI creates systems that learn from data. Neural networks are inspired by biological brains and use mathematical layers.",
  machine: "Machine learning teaches computers to learn from examples rather than explicit programming. It finds patterns in data.",
  neural: "Neural networks use layers of mathematical operations to learn patterns. They learn by adjusting weights during training.",
  transformer: "Transformers use attention mechanisms to process entire sequences at once - they revolutionized NLP and language AI!",
  gpt: "GPT uses transformers and large language models trained on vast text data to generate human-like responses.",
  github: "GitHub hosts code repositories and facilitates collaboration through pull requests, issues, and Actions.",
  git: "Git tracks changes in code, enabling version control. Use git add, commit, push, pull, merge for collaboration.",
  api: "APIs let applications communicate. REST APIs use HTTP methods: GET retrieves, POST creates, PUT updates, DELETE removes.",
  http: "HTTP is the web protocol. GET retrieves pages, POST sends data, PUT updates, DELETE removes resources.",
  server: "Servers provide services to clients. They listen on ports and respond to requests with data or web pages.",
  database: "Databases store structured data. SQL databases use tables with rows and columns. NoSQL uses documents or key-value pairs.",
  cloud: "Cloud computing provides resources on-demand. AWS, GCP, and Azure offer computing, storage, and AI services.",
  bug: "Bugs are errors in code. Debugging involves finding and fixing them using logs, tests, and careful analysis.",
  error: "Errors happen in code! Read error messages carefully - they usually tell you what's wrong and where.",
  function: "Functions organize code into reusable blocks. They accept inputs (parameters) and can return outputs.",
  class: "Classes define blueprints for objects in object-oriented programming. They package data and behavior together.",
  variable: "Variables store data values. They have names and types representing information that can change during execution.",
  loop: "Loops repeat code. Use for-loops for countable items, while-loops for conditions that may change.",
  array: "Arrays hold ordered lists of items. Access elements by index starting at 0 in most languages.",
  dictionary: "Dictionaries map keys to values for fast lookups. Also called maps, hash tables, or objects in different languages.",
  string: "Strings are text data. You can concatenate, split, search, and transform them in various ways.",
  number: "Numbers can be integers (whole numbers) or floats (decimals). Operations include addition, subtraction, multiplication, division.",
  boolean: "Booleans represent true or false. They control flow in if statements and while loops.",
  json: "JSON is a popular data format with key-value pairs. Easy for humans to read and machines to parse.",
  web: "The web uses HTTP to transfer HTML, CSS, JavaScript between servers and browsers worldwide.",
  internet: "The internet connects computers worldwide through protocols like TCP/IP, enabling global communication.",
  computer: "Computers follow instructions literally. They need exact, clear directions in ways they understand.",
  software: "Software includes applications, operating systems, and utilities that run on computer hardware.",
  data: "Data can be structured in databases or unstructured like text and images. Quality data drives better AI!",
  model: "Models learn patterns from training data. Better data with more examples leads to more accurate models.",
  train: "Training teaches models from examples. The model learns statistical patterns to make predictions on new data.",
  deploy: "Deployment publishes code so users can access it. Use platforms like Railway, Vercel, Heroku, or cloud providers.",
  test: "Testing validates code correctness. Use unit tests, integration tests, and end-to-end tests for confidence.",
  security: "Security protects systems from attacks. Use encryption, authentication, authorization, and follow best practices.",
  design: "Good design considers users, accessibility, performance, and maintainability. Iterate based on feedback.",
  start: "Great that you're starting! Pick a simple project and build it step by step. Learning by doing is effective.",
  help: "I'm here to help! Ask about programming, AI, web development, or any tech topic you're curious about.",
  who: "I'm AI-AGENT, an AI assistant built with a custom transformer model! I'm here to help and chat.",
  name: "I'm AI-AGENT, your helpful AI assistant! Built with love using transformers.",
  what: "I can help with programming, answer questions, explain tech concepts, and have conversations!",
  how: "I'll explain how things work! Just ask about any topic you're curious about and I'll share what I know.",
  why: "Great question! There are usually multiple reasons. Let me explain the key ones.",
  when: "That depends on context. Timing matters for software releases, learning paths, and deployment.",
  where: "Great resources exist online - documentation, MDN, Stack Overflow, tutorials, and developer communities.",
};

// Fallback responses - varied and engaging
const FALLBACK_RESPONSES = [
  "That's interesting! Tell me more about what you're working on.",
  "I'd love to hear more about your perspective on this.",
  "Great question! Here's what I know about that topic...",
  "That's a thoughtful angle. Let me share my thoughts.",
  "Interesting point! Here's another way to look at it.",
  "I'm curious - what specifically would you like to know?",
  "Tell me more! I want to understand your view.",
  "That's a cool topic. Here's my take...",
  "I can definitely help with that! More details please.",
  "Let's explore this together. What's your context?",
  // Greetings
  "Hey there! Great to chat. What shall we discuss?",
  "Hello! Ready to help. What's on your mind?",
  "Hi! Good to see you. Ask me anything!",
  // Encouragement
  "Keep exploring - that's how expertise develops!",
  "Great curiosity! Asking questions is how we learn.",
  "You're on the right track! Keep questioning.",
  // Programming
  "In programming, that typically involves breaking the problem into smaller parts.",
  "Code is just logic expressed in a way computers understand.",
  "Most solutions follow patterns - find the right one and apply it.",
  // Tech
  "Technology is always evolving. Staying current requires continuous learning.",
  "That's an important concept in tech. Here's the key idea...",
  "Modern systems often solve this with multiple layers.",
];

function getFallbackReply(message) {
  const m = message.toLowerCase();
  
  // Check specific keywords first
  for (const [keyword, response] of Object.entries(KEYWORD_RESPONSES)) {
    if (m.includes(keyword)) {
      return response;
    }
  }
  
  // Generic keyword patterns
  if (m.includes("hello") || m.includes("hi") || m.includes("hey") || m.includes("greetings")) {
    return "Hey there! Great to chat with you. What would you like to discuss?";
  }
  if (m.includes("help") || m.includes("assist")) {
    return "I'm here to help! Ask me about programming, AI, web dev, or any tech topic.";
  }
  if (m.includes("thank")) {
    return "You're welcome! Happy to help. What else can I answer?";
  }
  if (m.includes("bye") || m.includes("goodbye") || m.includes("see you")) {
    return "Goodbye! Great chatting with you. Come back anytime!";
  }
  if (m.includes("?")) {
    return "That's a great question! Let me share what I know about that.";
  }
  
  // Random engaging response
  return FALLBACK_RESPONSES[Math.floor(Math.random() * FALLBACK_RESPONSES.length)];
}

async function getModelReply(message) {
  try {
    const response = await fetch(`${FLASK_URL}/reply`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Flask service error");
    }

    return data.reply || getFallbackReply(message);
  } catch (error) {
    console.log("Using keyword response:", error.message);
    return getFallbackReply(message);
  }
}

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

    const reply = await getModelReply(cleanMessage);

    history.push({ role: "assistant", text: reply });

    res.json({ reply, history });
  } catch (error) {
    console.error(error);
    // Always return something instead of error
    res.json({ reply: getFallbackReply(req.body.message || "Hello"), history: [] });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
