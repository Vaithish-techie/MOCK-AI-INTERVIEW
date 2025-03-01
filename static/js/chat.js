function sendChatMessage(challengeIndex) {
  const inputField = document.getElementById(`chat-input-${challengeIndex}`);
  if (!inputField) return;
  const originalMessage = inputField.value.trim();
  if (!originalMessage) return;

  // Display user message
  addChatMessage(originalMessage, "user", challengeIndex);
  inputField.value = "";

  const lowerMsg = originalMessage.toLowerCase();
  if (isAtrocity(lowerMsg)) {
    addChatMessage("I'm sorry, but I cannot engage with that language.", "bot", challengeIndex);
    return;
  }
  if (isNonsense(lowerMsg)) {
    addChatMessage("Hmm... that doesn't seem related to the challenge. Need a hint or want to start coding?", "bot", challengeIndex);
    return;
  }

  // Send to AI
  fetch("/api/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: originalMessage })
  })
    .then(res => res.json())
    .then(data => {
      addChatMessage(data.response, "bot", challengeIndex);
    })
    .catch(err => {
      console.error(err);
      addChatMessage("Sorry, something went wrong. Please try again.", "bot", challengeIndex);
    });
}

function addChatMessage(text, sender, challengeIndex) {
  const chatBox = document.getElementById(`chat-box-${challengeIndex}`);
  if (!chatBox) return;
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.innerText = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function isAtrocity(msg) {
  const bannedWords = ["hate", "stupid", "idiot", "kill", "damn", "f***", "s***"];
  return bannedWords.some(w => msg.includes(w));
}

function isNonsense(msg) {
  const knownWords = ["code", "function", "start", "hint", "yes", "no", "done", "reverse", "palindrome"];
  return !knownWords.some(word => msg.includes(word));
}
