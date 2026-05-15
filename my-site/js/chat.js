// ── JARVIS Chat Client ──────────────────────────────────────

const input = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const messages = document.getElementById('chat-messages');
const typing = document.getElementById('typing-indicator');
const modelBadge = document.getElementById('model-badge');
const memStatus = document.getElementById('memory-status');
const clearBtn = document.getElementById('clear-memory-btn');
const canvas = document.getElementById('bg-canvas');
const quickActions = document.getElementById('quick-actions');

let history = []; // rolling chat history sent to server

// ── Canvas background (animated grid) ───────────────────────
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (canvas && !reduceMotion) {
  const ctx = canvas.getContext('2d');
  function resizeCanvas() {
    canvas.width = window.innerWidth * window.devicePixelRatio;
    canvas.height = window.innerHeight * window.devicePixelRatio;
    ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  let t = 0;
  function drawBg() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    ctx.strokeStyle = '#0d3a5c';
    ctx.lineWidth = 0.5;
    const spacing = 60;

    for (let x = 0; x < window.innerWidth; x += spacing) {
      ctx.globalAlpha = 0.25 + 0.1 * Math.sin(t * 0.01 + x * 0.01);
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, window.innerHeight); ctx.stroke();
    }
    for (let y = 0; y < window.innerHeight; y += spacing) {
      ctx.globalAlpha = 0.25 + 0.1 * Math.sin(t * 0.01 + y * 0.01);
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(window.innerWidth, y); ctx.stroke();
    }

    const scanY = (t * 1.2) % window.innerHeight;
    const grad = ctx.createLinearGradient(0, scanY - 60, 0, scanY + 60);
    grad.addColorStop(0, 'rgba(0,170,255,0)');
    grad.addColorStop(0.5, 'rgba(0,170,255,0.06)');
    grad.addColorStop(1, 'rgba(0,170,255,0)');
    ctx.globalAlpha = 1;
    ctx.fillStyle = grad;
    ctx.fillRect(0, scanY - 60, window.innerWidth, 120);

    t += 1;
    requestAnimationFrame(drawBg);
  }
  drawBg();
}

// ── Helpers ──────────────────────────────────────────────────
function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function addMessage(text, role, meta = '') {
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  let html = escapeHtml(text);
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
    `<pre><code>${code.trim()}</code></pre>`
  );
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  html = html.replace(/\n/g, '<br>');

  if (meta) html += `<span class="msg-meta">${escapeHtml(meta)}</span>`;
  div.innerHTML = html;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function setLoading(on) {
  typing.style.display = on ? 'flex' : 'none';
  sendBtn.disabled = on;
  input.disabled = on;
  if (!on) input.focus();
}

function setStatus(text, online = true) {
  const statusText = document.getElementById('status-text');
  const statusDot = document.getElementById('status-dot');
  if (statusText) statusText.textContent = text;
  if (statusDot) statusDot.classList.toggle('offline', !online);
}

// ── API helpers ──────────────────────────────────────────────
async function fetchJson(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 120000);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function checkHealth() {
  try {
    const health = await fetchJson('/health', { timeout: 5000 });
    setStatus('ONLINE', true);
    if (health.python?.tiny_model) modelBadge.textContent = 'tiny model ready';
    else if (health.defaultModel) modelBadge.textContent = health.defaultModel;
    else modelBadge.textContent = 'agent ready';
  } catch {
    setStatus('LIMITED', false);
    modelBadge.textContent = 'offline';
  }
}

// ── Send message ─────────────────────────────────────────────
async function send(text = input.value) {
  const msg = String(text).trim();
  if (!msg) return;

  addMessage(msg, 'user');
  input.value = '';
  setLoading(true);

  try {
    const data = await fetchJson('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, history }),
    });

    const reply = data.reply || 'No response received.';
    const model = data.model || data.source || '';
    addMessage(reply, 'jarvis', model ? `source: ${model}` : '');

    if (model) modelBadge.textContent = model;

    history.push({ role: 'user', content: msg });
    history.push({ role: 'assistant', content: reply });
    if (history.length > 20) history = history.slice(-20);

    updateMemoryStatus();
  } catch (err) {
    const reason = err.name === 'AbortError' ? 'request timed out' : err.message;
    addMessage(`Connection error: ${reason}. If you are using a preview, start the server first.`, 'jarvis');
    setStatus('LIMITED', false);
  } finally {
    setLoading(false);
  }
}

// ── Memory status ─────────────────────────────────────────────
async function updateMemoryStatus() {
  try {
    const mem = await fetchJson('/memory', { timeout: 5000 });
    const learnedCount = (mem.learned || []).length;
    const noteCount = (mem.notes || []).length;
    const factCount = Object.keys(mem.facts || {}).length;
    const count = learnedCount + noteCount + factCount;
    const name = mem.userName || mem.facts?.name;
    memStatus.textContent = `${name ? `User: ${name} · ` : ''}${count} memories`;
  } catch {
    memStatus.textContent = 'Memory active';
  }
}

clearBtn.addEventListener('click', async () => {
  if (!confirm('Clear all JARVIS memory?')) return;
  try {
    await fetchJson('/memory/clear', { method: 'POST', timeout: 5000 });
    history = [];
    messages.innerHTML = '';
    addMessage('Memory cleared. Ready for a fresh start.', 'jarvis');
    memStatus.textContent = '0 memories';
  } catch (err) {
    addMessage(`Could not clear memory: ${err.message}`, 'jarvis');
  }
});

// ── Event listeners ───────────────────────────────────────────
sendBtn.addEventListener('click', () => send());
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

quickActions.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-prompt]');
  if (!btn) return;
  send(btn.dataset.prompt);
});

// ── Init ──────────────────────────────────────────────────────
(async () => {
  addMessage('Systems online. Try calculator, memory, planner, or code help.', 'jarvis');
  await checkHealth();
  updateMemoryStatus();
})();
