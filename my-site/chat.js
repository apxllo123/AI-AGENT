document.addEventListener("DOMContentLoaded", () => {
  const chatButton = document.getElementById("home-cta__button");
  if (!chatButton) return;

  chatButton.addEventListener("click", (event) => {
    event.preventDefault();
    console.log("Start Chat clicked");
  });
});
