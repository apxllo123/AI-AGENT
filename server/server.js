const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

function getBotReply(message) {
  const text = message.toLowerCase();

  if (text.includes("hello") || text.includes("hi") || text.includes("hey")) {
    return "Hello! How can I help you today?";
  }

  if (text.includes("how are you")) {
    return "I’m doing great — thanks for asking. How are you?";
  }

  if (text.includes("what can you do")) {
    return "I can chat with you, answer simple questions, and help with your site.";
  }

  if (text.includes("help")) {
    return "Sure, tell me what you need help with.";
  }

  if (text.includes("thanks") || text.includes("thank you")) {
    return "You’re welcome!";
  }

  return "I’m not sure I understood that. Try asking me something simple like hello or what can you do.";
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
    history.push({ role: "user", text: message.trim() });

    const reply = getBotReply(message.trim());

    history.push({ role: "assistant", text: reply });

    res.json({ reply, history });
  } catch (error) {
    res.status(500).json({ error: "Server error" });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
