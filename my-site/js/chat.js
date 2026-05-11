// ── JARVIS Chat Client ──────────────────────────────────────

const input     = document.getElementById('chat-input');
const sendBtn   = document.getElementById('send-btn');
const messages  = document.getElementById('chat-messages');
const typing    = document.getElementById('typing-indicator');
const modelBadge = document.getElementById('model-badge');
const memStatus  = document.getElementById('memory-status');
const clearBtn   = document.getElementById('clear-memory-btn');
const canvas     = document.getElementById('bg-canvas');

let history = []; // rolling chat history sent to server

// ── Canvas background (animated grid) ───────────────────────
const ctx = canvas.getContext('2d');
function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

let t = 0;
function drawBg() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = '#0d3a5c';
  ctx.lineWidth = 0.5;
  const spacing = 60;

  // Grid
  for (let x = 0; x < canvas.width; x += spacing) {
    ctx.globalAlpha = 0.3 + 0.1 * Math.sin(t * 0.01 + x * 0.01);
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += spacing) {
    ctx.globalAlpha = 0.3 + 0.1 * Math.sin(t * 0.01 + y * 0.01);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
  }

  // Scan line
  const scanY = (t * 1.2) % canvas.height;
  const grad = ctx.createLinearGradient(0, scanY - 60, 0, scanY + 60);
  grad.addColorStop(0, 'rgba(0,170,255,0)');
  grad.addColorStop(0.5, 'rgba(0,170,255,0.06)');
  grad.addColorStop(1, 'rgba(0,170,255,0)');
  ctx.globalAlpha = 1;
  ctx.fillStyle = grad;
  ctx.fillRect(0, scanY - 60, canvas.width, 120);

  t++;
  requestAnimationFrame(drawBg);
}
drawBg();

// ── Helpers ──────────────────────────────────────────────────
function addMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  // Render markdown code blocks
  let html = escapeHtml(text);
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
    `<pre><code>${code.trim()}</code></pre>`
  );
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  html = html.replace(/\n/g, '<br>');

  div.innerHTML = html;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function setLoading(on) {
  typing.style.display = on ? 'flex' : 'none';
  sendBtn.disabled = on;
  input.disabled = on;
  if (!on) input.focus();
}

// ── Send message ─────────────────────────────────────────────
async function send() {
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, 'user');
  input.value = '';
  setLoading(true);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, history }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const reply = data.reply || 'No response received.';
    addMessage(reply, 'jarvis');

    if (data.model) modelBadge.textContent = data.model;

    // Update rolling history (keep last 10 pairs = 20 messages)
    history.push({ role: 'user', content: msg });
    history.push({ role: 'assistant', content: reply });
    if (history.length > 20) history = history.slice(-20);

    updateMemoryStatus();

  } catch (err) {
    addMessage(`Connection error: ${err.message}`, 'jarvis');
  }

  setLoading(false);
}

// ── Memory status ─────────────────────────────────────────────
async function updateMemoryStatus() {
  try {
    const res = await fetch('/memory');
    const mem = await res.json();
    const count = (mem.learned || []).length;
    const name = mem.userName ? `User: ${mem.userName} · ` : '';
    memStatus.textContent = `${name}${count} memories`;
  } catch {
    memStatus.textContent = 'Memory active';
  }
}

clearBtn.addEventListener('click', async () => {
  if (!confirm('Clear all JARVIS memory?')) return;
  await fetch('/memory/clear', { method: 'POST' });
  history = [];
  messages.innerHTML = '';
  addMessage('Memory cleared. Ready for a fresh start, sir.', 'jarvis');
  memStatus.textContent = '0 memories';
});

// ── Event listeners ───────────────────────────────────────────
sendBtn.addEventListener('click', send);
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });

// ── Init ──────────────────────────────────────────────────────
(async () => {
  addMessage('Good evening, sir. Systems online and operational. How may I assist you?', 'jarvis');
  updateMemoryStatus();
})();
