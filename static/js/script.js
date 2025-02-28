/*******************************************************
 * GLOBALS
 *******************************************************/
let totalMCQs = 0;
let answeredCount = 0;
window.twoChallenges = [];

/*******************************************************
 * 1) Screen Navigation
 *******************************************************/
function showScreen(id) {
  const screens = document.querySelectorAll(".screen");
  screens.forEach(scr => scr.classList.remove("active"));
  document.getElementById(id).classList.add("active");

  if (id === "round1") {
    fetchMCQs();
  } else if (id === "round2_challenge1") {
    // Load challenges if not already loaded
    if (window.twoChallenges.length === 0) {
      fetchBalancedChallenges();
    } else {
      initiateChatConversation(1);
    }
  } else if (id === "round2_challenge2") {
    // Ensure challenges are loaded and initiate chatbot for Challenge 2
    if (window.twoChallenges.length === 0) {
      fetchBalancedChallenges();
    } else {
      initiateChatConversation(2);
    }
  } else if (id === "results") {
    fetchFinalReport();
  }
}

function restartInterview() {
  showScreen("dashboard");
  window.twoChallenges = [];
  sessionStorage.clear(); // Clear sessionStorage to reset scores
}

/*******************************************************
 * 2) Round 1: MCQs
 *******************************************************/
async function fetchMCQs() {
  try {
    const response = await fetch("/api/get_general_qs");
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    const container = document.getElementById("mcq-container");
    const progressLabel = document.getElementById("mcq-progress");
    container.innerHTML = "";

    if (data.error) {
      document.getElementById("mcq-error").innerText = data.error || "Failed to fetch MCQs. Please try again.";
      return;
    }

    totalMCQs = data.mcqs.length;
    answeredCount = 0;
    updateMCQProgress();

    data.mcqs.forEach((mcq, index) => {
      container.innerHTML += `
        <div class="mcq-item" data-id="${mcq.id}">
          <h4>Q${index + 1}: ${mcq.question_text}</h4>
          <label><input type="radio" name="mcq-${mcq.id}" value="A"/> A: ${mcq.options[0]}</label>
          <label><input type="radio" name="mcq-${mcq.id}" value="B"/> B: ${mcq.options[1]}</label>
          <label><input type="radio" name="mcq-${mcq.id}" value="C"/> C: ${mcq.options[2]}</label>
          <label><input type="radio" name="mcq-${mcq.id}" value="D"/> D: ${mcq.options[3]}</label>
        </div>
      `;
    });

    const allRadios = container.querySelectorAll('input[type="radio"]');
    allRadios.forEach(radio => {
      radio.addEventListener("change", updateAnsweredCount);
    });
  } catch (error) {
    console.error("Fetch MCQs error:", error);
    document.getElementById("mcq-error").innerText = `Error fetching MCQs: ${error.message || "Unknown error. Please try again."}`;
  }
}

function updateAnsweredCount() {
  const container = document.getElementById("mcq-container");
  const mcqItems = container.querySelectorAll(".mcq-item");
  let count = 0;
  mcqItems.forEach(item => {
    const qid = item.getAttribute("data-id");
    const selected = item.querySelector(`input[name="mcq-${qid}"]:checked`);
    if (selected) count++;
  });
  answeredCount = count;
  updateMCQProgress();
}

function updateMCQProgress() {
  const progressLabel = document.getElementById("mcq-progress");
  progressLabel.textContent = `${answeredCount} / ${totalMCQs} Answered`;
}

async function submitMCQs() {
  const container = document.getElementById("mcq-container");
  const mcqItems = container.querySelectorAll(".mcq-item");
  let answers = [];

  mcqItems.forEach(item => {
    const qid = item.getAttribute("data-id");
    const selected = item.querySelector(`input[name="mcq-${qid}"]:checked`);
    answers.push({
      id: qid,
      selectedOption: selected ? selected.value : null
    });
  });

  try {
    const response = await fetch("/api/submit_mcqs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    if (data.error) {
      document.getElementById("mcq-error").innerText = data.error;
    } else {
      alert(`Round 1 Score: ${data.round1_score}/${totalMCQs}`);
      console.log("MCQ Score:", data.round1_score);
      sessionStorage.setItem("mcq_score", data.round1_score);
      showScreen("round2_challenge1"); // Navigate to Round 2 (Challenge 1) after submitting MCQs
    }
  } catch (error) {
    console.error("Submit MCQs error:", error);
    document.getElementById("mcq-error").innerText = `Error submitting MCQs: ${error.message || "Unknown error. Please try again."}`;
  }
}

/*******************************************************
 * 3) Round 2: Coding + Chat
 *******************************************************/
async function fetchBalancedChallenges() {
  try {
    // Clear previous conversation histories
    const clearResponse = await fetch("/api/clear_conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!clearResponse.ok) {
      console.error("Failed to clear conversations:", clearResponse.status);
    }

    const resp = await fetch("/api/balanced_coding_challenges");
    if (!resp.ok) {
      throw new Error(`HTTP error! Status: ${resp.status}`);
    }
    const data = await resp.json();
    if (data.error) {
      alert(data.error || "Failed to fetch challenges. Please try again.");
      return;
    }
    const challenges = data.challenges || [];
    if (challenges.length < 2) {
      alert("Could not fetch two challenges. Please try again.");
      return;
    }
    window.twoChallenges = challenges;
    fillChallenge(1, challenges[0]);
    fillChallenge(2, challenges[1]);
    initiateChatConversation(1); // Initiate chatbot for Challenge 1
  } catch (error) {
    console.error("Fetch challenges error:", error);
    alert(`Error fetching challenges: ${error.message || "Unknown error. Please try again."}`);
  }
}

function fillChallenge(index, challenge) {
  const questionCard = document.getElementById(`question-${index}-card`);
  if (!questionCard) return;
  questionCard.innerHTML = `
    <h3>Challenge ${index} of 2: ${challenge.title} (${challenge.difficulty})</h3>
    <p>${challenge.description}</p>
    <p><strong>Sample Input:</strong> ${challenge.sample_input}</p>
    <p><strong>Sample Output:</strong> ${challenge.sample_output}</p>
  `;
  // Add event listener for Enter key on chat input
  document.getElementById(`chat-input-${index}`).addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendChatMessage(index);
  });
}

async function runCode(index) {
  const codeInput = document.getElementById(`code-input-${index}`);
  const langSelect = document.getElementById(`language-select-${index}`);
  const outputBlock = document.getElementById(`output-block-${index}`);
  const resultDiv = document.getElementById(`execution-result-${index}`);

  const code = codeInput.value.trim();
  const language = langSelect.value;

  try {
    const response = await fetch("/api/submit_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    outputBlock.style.display = "block";
    resultDiv.innerHTML = `
      <p><strong>Output:</strong> ${data.output || "No output"}</p>
      <p><strong>Error:</strong> ${data.error || "No error"}</p>
      <p><strong>Execution Time:</strong> ${data.execution_time || "N/A"}</p>
    `;
    // Increment errors if there's an error in the output
    if (data.error) {
      sessionStorage.setItem("performance", JSON.stringify({
        ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
        errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
      }));
    }
    // Trigger chatbot feedback after running code
    const challengeContext = buildChallengeContext(index);
    autoChatAfterRun(data.output || data.error || "No output", challengeContext, index);
  } catch (error) {
    console.error("Run code error:", error);
    outputBlock.style.display = "block";
    resultDiv.innerHTML = `<p class="error">Error executing code: ${error.message || "Unknown error. Please try again."}</p>`;
    // Increment errors on failed execution
    sessionStorage.setItem("performance", JSON.stringify({
      ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
      errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
    }));
  }
}

async function analyzeCode(index) {
  const analyzeBtn = document.getElementById(`analyze-btn-${index}`);
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  const code = document.getElementById(`code-input-${index}`).value.trim();
  if (!code) {
    alert("Please write some code to analyze!");
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "AI Analysis";
    return;
  }

  try {
    const response = await fetch("/api/analyze_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    if (data.error) {
      addChatMessage("Sorry, I couldn’t analyze the code: " + data.error, "bot", `chat-box-${index}`);
    } else {
      addChatMessage(data.analysis, "bot", `chat-box-${index}`);
    }
  } catch (error) {
    console.error("Analysis error:", error);
    addChatMessage(`Sorry, I couldn’t analyze the code: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
  }
  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "AI Analysis";
}

async function submitCode(index) {
  const submitBtn = document.getElementById(`submit-btn-${index}`);
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";
  const code = document.getElementById(`code-input-${index}`).value.trim();
  const lang = document.getElementById(`language-select-${index}`).value;
  try {
    const response = await fetch("/api/submit_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language: lang })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    if (data.error) {
      alert(`Error: ${data.error}`);
      // Increment errors on failed submission
      sessionStorage.setItem("performance", JSON.stringify({
        ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
        errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
      }));
    } else {
      alert(data.output || "Submitted successfully!");
      sessionStorage.setItem(`coding_score_${index}`, "4"); // 4 points per challenge
      console.log(`Coding Score for Challenge ${index}:`, sessionStorage.getItem(`coding_score_${index}`));
      // Navigate based on which challenge was submitted
      if (index === 1) {
        showScreen("round2_challenge2");
      } else if (index === 2) {
        const codingScore = (parseInt(sessionStorage.getItem("coding_score_1") || 0) + 
                            parseInt(sessionStorage.getItem("coding_score_2") || 0));
        sessionStorage.setItem("coding_score", codingScore.toString());
        console.log("Total Coding Score:", codingScore);
        showScreen("results");
      }
    }
  } catch (error) {
    console.error("Submit code error:", error);
    alert(`Submission failed: ${error.message || "Unknown error. Please check your API key or network connection."}`);
    // Increment errors on failed submission
    sessionStorage.setItem("performance", JSON.stringify({
      ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
      errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
    }));
  }
  submitBtn.disabled = false;
  submitBtn.textContent = "Submit";
}

function addChatMessage(text, sender, chatBoxId) {
  const chatBox = document.getElementById(chatBoxId);
  if (!chatBox) return;
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearChat(chatBoxId) {
  const chatBox = document.getElementById(chatBoxId);
  if (chatBox) chatBox.innerHTML = "";
}

async function initiateChatConversation(index) {
  const challenge = window.twoChallenges[index - 1];
  const challengeContext = challenge ?
    `Challenge ${index} of 2: ${challenge.title} - ${challenge.description}\nSample Input: ${challenge.sample_input}\nSample Output: ${challenge.sample_output}` :
    "No challenge context available";
  try {
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Start the coding challenge interview.",
        challenge_context: challengeContext,
        challenge_id: index
      })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    addChatMessage(data.response, "bot", `chat-box-${index}`);
    // Follow up with "How can I help?"
    setTimeout(() => {
      addChatMessage("How can I help you with this challenge? For example, would you like a hint to get started?", "bot", `chat-box-${index}`);
    }, 1000);
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`Sorry, I couldn’t start the conversation: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
  }
}

async function autoChatAfterRun(runResult, challengeContext, index) {
  try {
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `The code execution result is: ${runResult}. Provide feedback and ask if the user needs further assistance.`,
        challenge_context: challengeContext,
        challenge_id: index
      })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    addChatMessage(data.response, "bot", `chat-box-${index}`);
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`I couldn’t analyze the run result: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
  }
}

async function sendChatMessage(index) {
  const inputField = document.getElementById(`chat-input-${index}`);
  const sendBtn = document.getElementById(`round2-send-btn-${index}`);
  const message = inputField.value.trim();
  if (!message) return;

  addChatMessage(message, "user", `chat-box-${index}`);
  inputField.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking...";

  const challenge = window.twoChallenges[index - 1];
  const challengeContext = challenge ?
    `Challenge ${index} of 2: ${challenge.title} - ${challenge.description}\nSample Input: ${challenge.sample_input}\nSample Output: ${challenge.sample_output}` :
    "No challenge context available";

  try {
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Technical: " + message,
        challenge_context: challengeContext,
        challenge_id: index
      })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    addChatMessage(data.response, "bot", `chat-box-${index}`);
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`Sorry, something went wrong: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
  }
  sendBtn.disabled = false;
  sendBtn.textContent = "Send";
}

function buildChallengeContext(index) {
  const challenge = window.twoChallenges[index - 1];
  if (!challenge) return "No challenge context";
  return `Title: ${challenge.title}\nDescription: ${challenge.description}\nSample Input: ${challenge.sample_input}\nSample Output: ${challenge.sample_output}`;
}

/*******************************************************
 * 4) Results
 *******************************************************/
async function fetchFinalReport() {
  try {
    const response = await fetch("/api/final_report");
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    const finalDiv = document.getElementById("final-report");

    if (data.error) {
      finalDiv.innerHTML = `<p class="error">${data.error || "Failed to fetch final report. Please try again."}</p>`;
      return;
    }
    finalDiv.innerHTML = `
      <p><strong>Overall Score:</strong> ${data.overall_score}/30</p>
      <p><strong>Time Limit:</strong> ${data.time_limit}</p>
      <h3>Category Scores</h3>
      <ul>
        <li><strong>MCQs:</strong> ${data.category_scores.MCQs}</li>
        <li><strong>Coding:</strong> ${data.category_scores.Coding}</li>
        <li><strong>Behavioral:</strong> ${data.category_scores.Behavioral}</li>
      </ul>
      <p><strong>Badges:</strong> ${data.badges.join(", ") || "None"}</p>
      <p><strong>Feedback:</strong> ${data.message}</p>
      <h4>Behavioral Feedback</h4>
      <ul>
        ${data.behavioral_feedback.map(f => `<li>${f}</li>`).join("")}
      </ul>
      ${data.transcript && data.transcript.length > 0 ? `
        <h4>Transcript</h4>
        <div>
          ${data.transcript.map(t => `<p><strong>${t.speaker}:</strong> ${t.message}</p>`).join("")}
        </div>
      ` : ""}
    `;
  } catch (error) {
    console.error("Fetch final report error:", error);
    document.getElementById("final-report").innerText = `Error fetching final report: ${error.message || "Unknown error. Please try again."}`;
  }
}

/*******************************************************
 * 5) Sidebar Toggle
 *******************************************************/
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("collapsed");
}
