document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("home-cta__button");
  const panel = document.getElementById("chat-panel");
  const messages = document.getElementById("chat-messages");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  function addMessage(text, type) {
    if (!messages) return;

    const bubble = document.createElement("div");
    bubble.className = `message ${type}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  if (button && panel && input) {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      panel.style.display = "block";
      input.focus();
    });
  }

  if (form && input) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const text = input.value.trim();
      if (!text) return;

      addMessage(text, "sent");
      input.value = "";

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: text,
            userId: "default",
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          addMessage(data.error || "Something went wrong.", "received");
          return;
        }

        addMessage(data.reply, "received");
      } catch (error) {
        addMessage("Server error. Please try again.", "received");
      }
    });
  }
});
