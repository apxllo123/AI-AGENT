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
// REAL AI GENERATION SYSTEM (Your custom model)
// ============================================

// Training data for your AI
const TRAINING_DATA = `
hello world how are you today i am doing well thanks for asking
hello world what is going on not much just building ai
hello world i am excited to learn ai it is amazing what you can build
hello world machine learning is so powerful you can teach computers
hello world neural networks are like digital brains they learn patterns
hello world transformers changed ai forever attention is amazing
hello world python is great for ai and data science
hello world javascript powers the web and node is awesome
hello world github hosts the best code repositories
hello world git tracks all your code changes
hello world apis connect different applications
hello world json is the most popular data format
hello world html creates web page structure
hello world css makes web pages beautiful
hello world web development is fun and rewarding
hello world coding is like writing instructions for computers
hello world functions organize code into reusable parts
hello world loops repeat code many times
hello world conditions make decisions in code
hello world variables store information for later
hello world arrays hold lists of items
hello world objects group related data together
hello world classes define new types of objects
hello world inheritance reuses code in classes
hello world databases store important data
hello world sql queries databases for data
hello world nosql databases are flexible
hello world cloud computing is very convenient
hello world servers run your applications
hello world localhost is your own computer
hello world ports let applications communicate
hello world http is the web protocol
hello world get and post are http methods
hello world rest apis are very popular
hello world authentication protects your app
hello world encryption keeps data secure
hello world https is secure http
hello world cookies store small data pieces
hello world sessions track user state
hello world testing makes code reliable
hello world bugs are errors in code
hello world debugging finds the bugs
hello world console logs help debug
hello world breakpoints stop code to inspect
hello world nodes are points in a network
hello world edges connect nodes together
hello world graphs show relationships
hello world algorithms solve problems efficiently
hello world complexity matters for speed
hello world big o notation measures efficiency
hello world recursion calls functions themselves
hello world stack manages function calls
hello world heap stores dynamic data
hello world pointers reference memory locations
hello world references are safer than pointers
hello world memory gets allocated and freed
hello world garbage collection reclaims memory
hello world languages have different strengths
hello world types define what data means
hello world types enforce correct usage
hello world compilation translates to machine code
hello world interpretation runs line by line
hello world JIT compiles during execution
hello world virtual machines run code
hello world containers package applications
hello world docker makes containers easy
hello world kubernetes manages containers at scale
hello world microservices are small services
hello world apis are service contracts
hello world http is a text protocol
hello world tcp ensures reliable delivery
hello world udp is faster but less reliable
hello world dns maps names to addresses
hello world domains are human readable names
hello world websites need hosting
hello world cdn makes sites very fast
hello world cache stores data temporarily
hello world redis is a fast cache database
hello world mongodb stores json documents
hello world postgresql is a powerful sql database
hello world mysql is popular and reliable
hello world sqlite is great for local apps
hello world firebase provides easy backend
hello world serverless runs code without servers
hello world lambdas are serverless functions
hello world functions as a service is powerful
hello world apis gateway manages apis
hello world authentication verifies identity
hello world authorization controls access
hello world oauth is standard for authorization
hello world jwt tokens carry claims securely
`.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);

// Build n-gram model from training data
function buildModel(data) {
  const model = {};
  for (const line of data) {
    const words = line.split(' ');
    for (let i = 0; i < words.length - 1; i++) {
      const key = words[i];
      const next = words[i + 1];
      if (!model[key]) model[key] = [];
      model[key].push(next);
    }
  }
  return model;
}

const ngramModel = buildModel(TRAINING_DATA);
const vocab = Object.keys(ngramModel);

// Generate response using your model
function generateResponse(prompt, maxWords = 30) {
  const words = prompt.toLowerCase().split(' ').filter(w => w.length > 0);
  let current = words[words.length - 1] || 'hello';
  const response = [current];
  
  // Try to find a starting word that exists in our model
  for (let i = words.length - 1; i >= 0; i--) {
    if (ngramModel[words[i]]) {
      current = words[i];
      break;
    }
  }
  
  // Generate word by word using n-gram probabilities
  for (let i = 0; i < maxWords; i++) {
    const nextOptions = ngramModel[current];
    if (!nextOptions || nextOptions.length === 0) {
      // Try random word from vocabulary
      current = vocab[Math.floor(Math.random() * vocab.length)] || 'world';
    } else {
      current = nextOptions[Math.floor(Math.random() * nextOptions.length)];
    }
    
    if (!current || current === undefined) break;
    response.push(current);
    
    // Stop at sentence endings
    if (current.endsWith('.') || current.endsWith('!') || current.endsWith('?')) break;
  }
  
  let result = response.join(' ');
  
  // Clean up the response
  result = result.replace(/\s+/g, ' ').trim();
  result = result.charAt(0).toUpperCase() + result.slice(1);
  
  // Ensure it ends properly
  if (!result.match(/[.!?]$/)) {
    if (result.length > 20) result += '.';
    else result += '!';
  }
  
  return result;
}

// Fallback keyword responses (still useful for specific topics)
const KEYWORD_RESPONSES = {
  python: "Python is a versatile programming language great for AI, web development, and data science. It has libraries like NumPy, PyTorch, Flask, Django, and pandas.",
  javascript: "JavaScript powers the web! It's used for interactive websites, web apps, and servers with Node.js.",
  html: "HTML provides semantic structure for web pages using tags like <div>, <span>, <p>.",
  css: "CSS styles web pages - colors, layouts, fonts. Use Flexbox and Grid for layouts.",
  ai: "AI creates systems that learn from data. Neural networks are inspired by biological brains.",
  "machine learning": "Machine learning teaches computers to learn from examples rather than explicit programming.",
  neural: "Neural networks use layers to learn patterns. They learn by adjusting weights during training.",
  transformer: "Transformers use attention mechanisms - they revolutionized NLP and language AI!",
  gpt: "GPT uses transformers and large language models trained on vast text data.",
  github: "GitHub hosts code repositories and facilitates collaboration through pull requests.",
  git: "Git tracks changes in code. Use git add, commit, push, pull, merge.",
  api: "APIs let applications communicate. REST uses HTTP methods: GET, POST, PUT, DELETE.",
  http: "HTTP is the web protocol. GET retrieves, POST creates, PUT updates, DELETE removes.",
  server: "Servers provide services to clients. They listen on ports and respond to requests.",
  database: "Databases store structured data. SQL uses tables. NoSQL uses documents or key-value.",
  cloud: "Cloud computing provides resources on-demand. AWS, GCP, and Azure offer great services.",
  bug: "Bugs are errors in code. Debug involves finding and fixing them.",
  error: "Errors happen! Read error messages carefully - they tell you what's wrong.",
  function: "Functions organize code into reusable blocks with inputs and outputs.",
  class: "Classes define blueprints for objects in object-oriented programming.",
  variable: "Variables store data values that can change during execution.",
  loop: "Loops repeat code. Use for-loops for count, while-loops for conditions.",
  array: "Arrays hold ordered lists of items. Access by index starting at 0.",
  dictionary: "Dictionaries map keys to values for fast lookups.",
  string: "Strings are text data. You can concatenate, split, search.",
  json: "JSON is a popular data format with key-value pairs.",
  web: "The web uses HTTP to transfer content between servers and browsers.",
  learn: "Learning takes practice! Start with basics and build projects.",
  help: "I'm here to help! Ask about programming, AI, or any tech topic.",
  who: "I'm AI-AGENT, an AI assistant built with my own custom n-gram model!",
  name: "I'm AI-AGENT, your AI assistant running on a custom-trained model.",
  start: "Great that you're starting! Pick a simple project and build it step by step.",
};

function getSmartReply(message) {
  const m = message.toLowerCase();
  
  // Check for specific keywords first
  for (const [keyword, response] of Object.entries(KEYWORD_RESPONSES)) {
    if (m.includes(keyword)) return response;
  }
  
  // Use your real AI model for generation!
  try {
    const generated = generateResponse(m, 20 + Math.floor(Math.random() * 15));
    if (generated && generated.length > 10) return generated;
  } catch (e) {
    console.log('Generation error:', e.message);
  }
  
  // Fallback responses if generation fails
  const fallbacks = [
    "That's interesting! Tell me more about what you're working on.",
    "I'd love to hear more about your perspective.",
    "Great question! Here's what I know...",
    "Interesting point! Let me share my thoughts.",
    "I'm curious - what specifically would you like to know?",
  ];
  return fallbacks[Math.floor(Math.random() * fallbacks.length)];
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

    // Use your AI to generate the reply!
    const reply = getSmartReply(cleanMessage);

    history.push({ role: "assistant", text: reply });
    res.json({ reply, history });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Sorry, I had an issue generating a response." });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`AI-AGENT server running on port ${PORT}`);
  console.log(`Your custom n-gram model loaded with ${vocab.length} vocabulary words`);
});
