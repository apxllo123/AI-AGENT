const { test, before, after } = require("node:test");
const assert = require("node:assert");
const { spawn } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SERVER = path.join(ROOT, "server", "server.js");
const TOKEN = "test-token-1234567890";
const ALLOWED = "https://allowed.example";

function startServer(port, extraEnv) {
  return spawn(process.execPath, [SERVER], {
    cwd: ROOT,
    env: { ...process.env, PORT: String(port), USE_OLLAMA: "false", ...extraEnv },
    stdio: ["ignore", "pipe", "pipe"],
  });
}

async function waitForHealth(port, child) {
  for (let i = 0; i < 100; i++) {
    if (child.exitCode !== null) throw new Error("server exited before becoming healthy");
    try {
      const res = await fetch("http://127.0.0.1:" + port + "/health");
      if (res.ok) return;
    } catch (_) {
      // server is not ready yet
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("server did not become healthy");
}

let tokenServer;
let originServer;
const TOKEN_PORT = 8231;
const ORIGIN_PORT = 8232;

before(async () => {
  tokenServer = startServer(TOKEN_PORT, { ACCESS_TOKEN: TOKEN });
  originServer = startServer(ORIGIN_PORT, {
    ACCESS_TOKEN: TOKEN,
    ALLOWED_ORIGINS: ALLOWED,
  });
  await Promise.all([
    waitForHealth(TOKEN_PORT, tokenServer),
    waitForHealth(ORIGIN_PORT, originServer),
  ]);
});

after(() => {
  if (tokenServer) tokenServer.kill();
  if (originServer) originServer.kill();
});

test("private routes reject requests without a token", async () => {
  const base = "http://127.0.0.1:" + TOKEN_PORT;
  const cases = [
    ["GET", "/memory"],
    ["POST", "/memory/clear"],
    ["GET", "/conversations"],
    ["POST", "/chat"],
  ];
  for (const [method, route] of cases) {
    const res = await fetch(base + route, { method });
    assert.strictEqual(res.status, 401, method + " " + route + " returned " + res.status);
  }
});

test("private routes accept the configured token", async () => {
  const base = "http://127.0.0.1:" + TOKEN_PORT;
  const memory = await fetch(base + "/memory", {
    headers: { Authorization: "Bearer " + TOKEN },
  });
  assert.strictEqual(memory.status, 200);
  const conversations = await fetch(base + "/conversations", {
    headers: { "X-Auth-Token": TOKEN },
  });
  assert.strictEqual(conversations.status, 200);
});

test("a wrong token is rejected", async () => {
  const res = await fetch("http://127.0.0.1:" + TOKEN_PORT + "/memory", {
    headers: { Authorization: "Bearer not-the-token" },
  });
  assert.strictEqual(res.status, 401);
});

test("the health route stays open", async () => {
  const res = await fetch("http://127.0.0.1:" + TOKEN_PORT + "/health");
  assert.strictEqual(res.status, 200);
});

test("an unlisted browser origin gets no CORS grant", async () => {
  const res = await fetch("http://127.0.0.1:" + ORIGIN_PORT + "/health", {
    headers: { Origin: "https://evil.example" },
  });
  assert.strictEqual(res.headers.get("access-control-allow-origin"), null);
});

test("a listed browser origin gets a CORS grant", async () => {
  const res = await fetch("http://127.0.0.1:" + ORIGIN_PORT + "/health", {
    headers: { Origin: ALLOWED },
  });
  assert.strictEqual(res.headers.get("access-control-allow-origin"), ALLOWED);
});
