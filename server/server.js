const express = require("express");
const cors = require("cors");
const path = require("path");
const { spawn } = require("child_process");

const app = express();

app.use(cors());
app.use(express.json());

const sitePath = path.join(__dirname, "../my-site");
app.use(express.static(sitePath));

const chatHistory = new Map();

function getModelReply(message) {
  return new Promise((resolve, reject) => {
    const py = spawn("python3", [path.join(__dirname, "reply.py"), message], {
      cwd: __dirname,
      stdio: ["ignore", "pipe", "pipe"]
    });

    let output = "";
    let error = "";

    py.stdout.on("data", (data) => {
      output += data.toString();
    });

    py.stderr.on("data", (data) => {
      error += data.toString();
    });

    py.on("error", (err) => {
      reject(err);
    });

    py.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(error || `Python exited with code ${code}`));
        return;
      }
      resolve(output.trim() || "I’m not sure how to reply to that.");
    });
  });
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
