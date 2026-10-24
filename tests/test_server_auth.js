const { test, before, after } = require("node:test");
const assert = require("node:assert");
const { spawn } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SERVER = path.join(ROOT, "server", "server.js");
const TOKEN = "test-token-1234567890";

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
      const res = await fetch(`http://127.0.0.1:${port}/health`);
      if (res.ok) return;
    } catch (_) {
      // server not ready yet
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("server did not become healthy");
}

let tokenServer;
const TOKEN_PORT = 8231;

before(async () => {
  tokenServer = startServer(TOKEN_PORT, { HOST: "127.0.0.1", AUTH_TOKEN: TOKEN });
  await waitForHealth(TOKEN_PORT, tokenServer);
});

after(() => {
  if (tokenServer) tokenServer.kill();
});

test("private routes reject requests without a token", async () => {
  const base = `http://127.0.0.1:${TOKEN_PORT}`;
  const cases = [
    ["GET", "/memory"],
    ["POST", "/memory/clear"],
    ["GET", "/conversations"],
    ["POST", "/chat"],
  ];
  for (const [method, route] of cases) {
    const res = await fetch(base + route, { method });
    assert.strictEqual(res.status, 401, `${method} ${route} returned ${res.status}`);
  }
});

test("private routes accept the shared token", async () => {
  const base = `http://127.0.0.1:${TOKEN_PORT}`;
  const memory = await fetch(base + "/memory", {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  assert.strictEqual(memory.status, 200);
  const conversations = await fetch(base + "/conversations", {
    headers: { "X-Auth-Token": TOKEN },
  });
  assert.strictEqual(conversations.status, 200);
});

test("a wrong token is rejected", async () => {
  const res = await fetch(`http://127.0.0.1:${TOKEN_PORT}/memory`, {
    headers: { Authorization: "Bearer not-the-token" },
  });
  assert.strictEqual(res.status, 401);
});

test("a token is still required when AUTH_TOKEN is unset", async () => {
  const port = 8232;
  const child = startServer(port, { HOST: "127.0.0.1", AUTH_TOKEN: "" });
  try {
    await waitForHealth(port, child);
    const memory = await fetch(`http://127.0.0.1:${port}/memory`);
    assert.strictEqual(memory.status, 401);
    const health = await fetch(`http://127.0.0.1:${port}/health`);
    assert.strictEqual(health.status, 200);
  } finally {
    child.kill();
  }
});

test("the server binds loopback by default", async () => {
  const port = 8233;
  const child = startServer(port, { AUTH_TOKEN: TOKEN, HOST: "" });
  try {
    await waitForHealth(port, child);
    const res = await fetch(`http://127.0.0.1:${port}/health`);
    assert.strictEqual(res.status, 200);
  } finally {
    child.kill();
  }
});
