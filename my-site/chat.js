document.addEventListener("DOMContentLoaded", () => {
  const chatButton = document.querySelector("#home-cta a");
  if (!chatButton) return;

  chatButton.addEventListener("click", (event) => {
    event.preventDefault();
    console.log("Open chat here");
  });
});
