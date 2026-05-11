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

const FALLBACK_RESPONSES = [
  "Hello! I'm your AI assistant. How can I help you today?",
  "That's interesting! Tell me more.",
  "I'm here to chat with you!",
  "Thanks for the message!",
  "Hey there! Nice to hear from you!",
];

function getFallbackReply(message) {
  const m = message.toLowerCase();
  if (m.includes("hello") || m.includes("hi") || m.includes("hey")) {
    return "Hello! How can I help you today?";
  }
  if (m.includes("help")) {
    return "I'm here to assist you!";
  }
  if (m.includes("name")) {
    return "I'm AI-AGENT, your assistant!";
  }
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

    return data.reply || "I'm not sure how to reply to that.";
  } catch (error) {
    console.log("Flask unavailable, using fallback:", error.message);
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
    res.status(500).json({ error: error.message || "Server error" });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
