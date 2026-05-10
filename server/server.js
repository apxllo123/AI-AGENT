const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

const chatHistory = new Map();

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

    const reply = `You said: ${message.trim()}`;

    history.push({ role: "assistant", text: reply });

    res.json({
      reply,
      history,
    });
  } catch (error) {
    res.status(500).json({ error: "Server error" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
