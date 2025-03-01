/*******************************************************
 * GLOBALS
 *******************************************************/
let totalMCQs = 0;
let answeredCount = 0;
window.twoChallenges = [];

// Track the start time when the interview begins
if (!sessionStorage.getItem("start_time")) {
  sessionStorage.setItem("start_time", Date.now().toString());
}

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
  // Reset start time for a new interview
  sessionStorage.setItem("start_time", Date.now().toString());
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
    console.log("Submit MCQs response:", data);
    if (data.error) {
      document.getElementById("mcq-error").innerText = data.error;
    } else {
      const totalQuestions = data.total_questions !== undefined ? data.total_questions : totalMCQs;
      alert(`Round 1 Score: ${data.round1_score}/${totalQuestions}`);
      console.log("MCQ Score (raw):", data.round1_score);
      console.log("MCQ Score (normalized):", data.normalized_score);
      sessionStorage.setItem("mcq_score", data.normalized_score.toString());
      showScreen("round2_challenge1");
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
    initiateChatConversation(1);
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
  document.getElementById(`chat-input-${index}`).addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendChatMessage(index);
  });
}

async function runCode(index) {
  const codeInput = document.getElementById(`code-input-${index}`);
  const langSelect = document.getElementById(`language-select-${index}`);
  const outputBlock = document.getElementById(`output-block-${index}`);
  const resultDiv = document.getElementById(`execution-result-${index}`);
  const chatBox = document.getElementById(`chat-box-${index}`);

  const code = codeInput.value.trim();
  const language = langSelect.value;

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

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
    if (data.error) {
      sessionStorage.setItem("performance", JSON.stringify({
        ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
        errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
      }));
    }
    const challengeContext = buildChallengeContext(index);
    await autoChatAfterRun(data.output || data.error || "No output", challengeContext, index);
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (error) {
    console.error("Run code error:", error);
    outputBlock.style.display = "block";
    resultDiv.innerHTML = `<p class="error">Error executing code: ${error.message || "Unknown error. Please try again."}</p>`;
    sessionStorage.setItem("performance", JSON.stringify({
      ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
      errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
    }));
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }
}

async function analyzeCode(index) {
  const analyzeBtn = document.getElementById(`analyze-btn-${index}`);
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  const code = document.getElementById(`code-input-${index}`).value.trim();
  const chatBox = document.getElementById(`chat-box-${index}`);

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

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
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (error) {
    console.error("Analysis error:", error);
    addChatMessage(`Sorry, I couldn’t analyze the code: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
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
  const chatBox = document.getElementById(`chat-box-${index}`);

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

  try {
    // Submit the code for execution
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
      sessionStorage.setItem("performance", JSON.stringify({
        ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
        errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
      }));
    } else {
      // Get AI feedback after execution
      const challengeContext = buildChallengeContext(index);
      await autoChatAfterRun(data.output || "No output", challengeContext, index);

      // Retrieve the AI's response from sessionStorage
      const botResponse = sessionStorage.getItem(`bot_response_${index}`) || "No feedback available";

      // Evaluate the code quality using the AI response
      const evalResponse = await fetch("/api/evaluate_code_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bot_response: botResponse })
      });
      if (!evalResponse.ok) {
        throw new Error(`HTTP error! Status: ${evalResponse.status}`);
      }
      const evalData = await evalResponse.json();
      const codingScore = evalData.code_score; // Score out of 10

      // Store the AI-evaluated score for the individual challenge
      sessionStorage.setItem(`coding_score_${index}`, codingScore.toString());
      console.log(`Coding Score for Challenge ${index}:`, codingScore);
      alert(`Challenge ${index} submitted successfully! Score: ${codingScore}/10`);

      // Calculate total coding score after each submission
      const codingScoreChallenge1 = parseInt(sessionStorage.getItem("coding_score_1") || 0);
      const codingScoreChallenge2 = parseInt(sessionStorage.getItem("coding_score_2") || 0);
      const totalCodingScore = codingScoreChallenge1 + codingScoreChallenge2; // Out of 20
      sessionStorage.setItem("coding_score", totalCodingScore.toString());
      console.log(`Updated Total Coding Score after Challenge ${index}:`, totalCodingScore);

      if (index === 1) {
        showScreen("round2_challenge2");
      } else if (index === 2) {
        showScreen("results");
      }
    }
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (error) {
    console.error("Submit code error:", error);
    alert(`Submission failed: ${error.message || "Unknown error. Please check your API key or network connection."}`);
    sessionStorage.setItem("performance", JSON.stringify({
      ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
      errors: (JSON.parse(sessionStorage.getItem("performance") || "{}").errors || 0) + 1
    }));
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }
  submitBtn.disabled = false;
  submitBtn.textContent = "Submit";
}

function addChatMessage(text, sender, chatBoxId) {
  const chatBox = document.getElementById(chatBoxId);
  if (!chatBox) return;

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);

  if (isScrolledToBottom) {
    chatBox.scrollTop = chatBox.scrollHeight;
  }
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
  const chatBox = document.getElementById(`chat-box-${index}`);

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

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
    setTimeout(() => {
      addChatMessage("How can I help you with this challenge? For example, would you like a hint to get started?", "bot", `chat-box-${index}`);
    }, 1000);

    // Store conversation in sessionStorage (only significant messages)
    const historyKey = `conversation_history_${index}`;
    let conversationHistory = sessionStorage.getItem(historyKey) ? JSON.parse(sessionStorage.getItem(historyKey)) : [];
    conversationHistory.push({"role": "assistant", "content": data.response});
    sessionStorage.setItem(historyKey, JSON.stringify(conversationHistory));
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`Sorry, I couldn’t start the conversation: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }
}

async function autoChatAfterRun(runResult, challengeContext, index) {
  const chatBox = document.getElementById(`chat-box-${index}`);

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

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
    sessionStorage.setItem(`bot_response_${index}`, data.response);

    // Store conversation in sessionStorage (only significant messages)
    const historyKey = `conversation_history_${index}`;
    let conversationHistory = sessionStorage.getItem(historyKey) ? JSON.parse(sessionStorage.getItem(historyKey)) : [];
    if (!data.response.toLowerCase().includes("hint")) {
      conversationHistory.push({"role": "assistant", "content": data.response});
      sessionStorage.setItem(historyKey, JSON.stringify(conversationHistory));
    }

    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`I couldn’t analyze the run result: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }
}

async function sendChatMessage(index) {
  const inputField = document.getElementById(`chat-input-${index}`);
  const sendBtn = document.getElementById(`round2-send-btn-${index}`);
  const message = inputField.value.trim();
  const chatBox = document.getElementById(`chat-box-${index}`);

  const isScrolledToBottom = chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;

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
    if (message.toLowerCase().includes("hint")) {
      sessionStorage.setItem("performance", JSON.stringify({
        ...JSON.parse(sessionStorage.getItem("performance") || "{}"),
        hints: (JSON.parse(sessionStorage.getItem("performance") || "{}").hints || 0) + 1
      }));
    }
    addChatMessage(data.response, "bot", `chat-box-${index}`);

    // Store conversation in sessionStorage (only significant messages)
    const historyKey = `conversation_history_${index}`;
    let conversationHistory = sessionStorage.getItem(historyKey) ? JSON.parse(sessionStorage.getItem(historyKey)) : [];
    if (!message.toLowerCase().includes("hint") && !message.includes("Technical: yes")) {
      conversationHistory.push({"role": "user", "content": message});
    }
    if (!data.response.toLowerCase().includes("hint")) {
      conversationHistory.push({"role": "assistant", "content": data.response});
    }
    sessionStorage.setItem(historyKey, JSON.stringify(conversationHistory));

    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (error) {
    console.error("Chat error:", error);
    addChatMessage(`Sorry, something went wrong: ${error.message || "Unknown error. Please try again."}`, "bot", `chat-box-${index}`);
    if (isScrolledToBottom) {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
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
  const finalDiv = document.getElementById("final-report");
  finalDiv.innerHTML = `
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Processing your results...</p>
    </div>
  `;

  try {
    // Retrieve scores from sessionStorage
    const mcqScore = parseInt(sessionStorage.getItem("mcq_score") || 0);
    const codingScore = parseInt(sessionStorage.getItem("coding_score") || 0);
    const behavioralScore = parseInt(sessionStorage.getItem("behavioral_score") || 0);

    // Calculate time_taken (in minutes)
    const startTime = parseInt(sessionStorage.getItem("start_time") || Date.now());
    const endTime = Date.now();
    const timeTakenMinutes = Math.round((endTime - startTime) / (1000 * 60)); // Convert milliseconds to minutes

    // Update performance object with time_taken
    let performance = JSON.parse(sessionStorage.getItem("performance") || "{}");
    performance.time_taken = timeTakenMinutes;
    sessionStorage.setItem("performance", JSON.stringify(performance));

    // Debug: Log scores before sending to backend
    console.log("Scores before sending to backend - MCQ:", mcqScore, "Coding (total, out of 20):", codingScore, "Behavioral:", behavioralScore, "Time Taken (minutes):", timeTakenMinutes);

    // Send scores to backend
    const response = await fetch("/api/final_report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mcq_score: mcqScore,
        coding_score: codingScore,
        behavioral_score: behavioralScore,
        transcript_1: sessionStorage.getItem("conversation_history_1") ? JSON.parse(sessionStorage.getItem("conversation_history_1")) : [],
        transcript_2: sessionStorage.getItem("conversation_history_2") ? JSON.parse(sessionStorage.getItem("conversation_history_2")) : [],
        performance: performance
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();

    if (data.error) {
      finalDiv.innerHTML = `<p class="error">${data.error || "Failed to fetch final report. Please try again."}</p>`;
      return;
    }

    // Debug: Log fetched data
    console.log("Fetched Data from Backend:", data);
    console.log("Coding Score from Backend (should match total, out of 20):", data.category_scores.Coding);

    // Filter transcript to show only significant interactions
    const filteredTranscript = data.transcript ? data.transcript.filter(t => 
      t.message.includes("The code execution result is") || // AI feedback after code run
      t.message.includes("Challenge submitted successfully") || // Submission confirmation
      !t.message.toLowerCase().includes("hint") // Exclude hint requests
    ) : [];

    // Update the DOM with the fetched data
    finalDiv.innerHTML = `
      <div class="score-section">
        <p><strong>Overall Score:</strong> <span id="overall-score">${data.overall_score}/30</span></p>
        <div class="progress-bar">
          <div id="overall-progress" class="progress-fill" style="width: ${(data.overall_score / 30) * 100}%"></div>
        </div>
      </div>

      <h3>Category Scores</h3>
      <canvas id="category-scores-chart" width="400" height="200"></canvas>

      <h3>Performance Metrics</h3>
      <canvas id="performance-metrics-chart" width="400" height="300"></canvas>

      <h3>Your Achievements</h3>
      <div id="badges-section" class="badges-container"></div>

      <h3>Performance Analysis</h3>
      <div id="ai-analysis"></div>

      <h3>Leaderboard</h3>
      <ul id="leaderboard" class="leaderboard"></ul>

      <div id="transcript-section">
        <h4>Transcript <button id="toggle-transcript" onclick="toggleTranscript()">Show/Hide</button></h4>
        <div id="transcript-content" style="display: none;"></div>
      </div>
    `;

    // Render Category Scores Bar Chart
    const categoryCtx = document.getElementById("category-scores-chart").getContext("2d");
    const codingScoreNormalized = Math.round((parseInt(data.category_scores.Coding) || 0) / 2); // Normalize from 0-20 to 0-10
    console.log("Bar Graph Data - MCQs:", parseInt(data.category_scores.MCQs), "Coding (normalized, out of 10):", codingScoreNormalized, "Behavioral:", parseInt(data.category_scores.Behavioral));
    new Chart(categoryCtx, {
      type: "bar",
      data: {
        labels: ["MCQs", "Coding", "Behavioral"],
        datasets: [{
          label: "Score (out of 10)",
          data: [
            parseInt(data.category_scores.MCQs) || 0,
            codingScoreNormalized,
            parseInt(data.category_scores.Behavioral) || 0
          ],
          backgroundColor: [
            "rgba(108, 99, 255, 0.7)",
            "rgba(74, 66, 179, 0.7)",
            "rgba(40, 35, 102, 0.7)"
          ],
          borderColor: [
            "rgba(108, 99, 255, 1)",
            "rgba(74, 66, 179, 1)",
            "rgba(40, 35, 102, 1)"
          ],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 10,
            ticks: {
              color: "#ccc",
              stepSize: 2
            },
            grid: {
              color: "rgba(255, 255, 255, 0.1)"
            }
          },
          x: {
            ticks: {
              color: "#ccc"
            },
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${context.raw}/10`;
              }
            }
          }
        }
      }
    });

    // Render Performance Metrics Radar Chart with Tooltips
    const performanceCtx = document.getElementById("performance-metrics-chart").getContext("2d");
    const performanceData = JSON.parse(sessionStorage.getItem("performance") || "{}");
    const hintsUsed = parseInt(performanceData.hints) || 0;
    const errorsMade = parseInt(performanceData.errors) || 0;
    const timeTaken = parseInt(performanceData.time_taken) || 0;
    const radarData = [
      hintsUsed, // Raw value for Hints Used
      errorsMade, // Raw value for Errors Made
      timeTaken  // Raw value for Time Taken (in minutes)
    ];
    new Chart(performanceCtx, {
      type: "radar",
      data: {
        labels: ["Hints Used", "Errors Made", "Time Taken (min)"],
        datasets: [{
          label: "Performance Metrics",
          data: [
            hintsUsed / 5, // Normalized to 0-5 scale
            errorsMade / 5, // Normalized to 0-5 scale
            timeTaken / 90 * 5 // Normalized to 0-5 scale (90 min max)
          ],
          backgroundColor: "rgba(108, 99, 255, 0.2)",
          borderColor: "rgba(108, 99, 255, 1)",
          borderWidth: 2,
          pointBackgroundColor: "rgba(108, 99, 255, 1)"
        }]
      },
      options: {
        scales: {
          r: {
            beginAtZero: true,
            max: 5,
            ticks: {
              stepSize: 1,
              color: "#ccc",
              backdropColor: "rgba(0, 0, 0, 0)"
            },
            grid: {
              color: "rgba(255, 255, 255, 0.1)"
            },
            angleLines: {
              color: "rgba(255, 255, 255, 0.1)"
            },
            pointLabels: {
              color: "#ccc"
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const rawValue = radarData[context.dataIndex];
                if (label === "Hints Used") {
                  return `${label}: ${rawValue} hint(s)`;
                } else if (label === "Errors Made") {
                  return `${label}: ${rawValue} error(s)`;
                } else if (label === "Time Taken (min)") {
                  return `${label}: ${rawValue} minute(s)`;
                }
                return `${label}: ${rawValue}`;
              }
            }
          }
        }
      }
    });

    // Add a caption below the radar chart
    const performanceMetricsChart = document.getElementById("performance-metrics-chart");
    const caption = document.createElement("div");
    caption.className = "chart-caption";
    caption.innerHTML = `
      <p>Hints Used: Number of hints requested during coding challenges.</p>
      <p>Errors Made: Number of code execution errors encountered.</p>
      <p>Time Taken: Total time taken for the interview (in minutes).</p>
    `;
    performanceMetricsChart.parentNode.insertBefore(caption, performanceMetricsChart.nextSibling);

    // Badges Section with Gamification
    const badgesDiv = document.getElementById("badges-section");
    badgesDiv.innerHTML = "";
    data.badges.forEach(badge => {
      const badgeIcon = getBadgeIcon(badge);
      badgesDiv.innerHTML += `
        <div class="badge">
          <span class="badge-icon">${badgeIcon}</span>
          <span>${badge}</span>
        </div>
      `;
    });

    // AI-Driven Analysis in Bullet Points
    const analysisDiv = document.getElementById("ai-analysis");
    const analysisPoints = parseAnalysisToPoints(data.message);
    analysisDiv.innerHTML = `
      <ul class="analysis-list">
        ${analysisPoints.map(point => `<li>${point.replace(/^-\s*/, '')}</li>`).join("")}
      </ul>
    `;

    // Leaderboard
    const leaderboardDiv = document.getElementById("leaderboard");
    leaderboardDiv.innerHTML = "";
    data.leaderboard.forEach(entry => {
      leaderboardDiv.innerHTML += `
        <li class="${entry.name === 'You' ? 'highlight' : ''}">
          ${entry.name}: ${entry.totalScore}/30
        </li>
      `;
    });

    // Transcript (Optional)
    const transcriptDiv = document.getElementById("transcript-content");
    const transcriptSection = document.getElementById("transcript-section");
    if (filteredTranscript.length > 0) {
      transcriptDiv.innerHTML = filteredTranscript.map(t => `<p><strong>${t.speaker}:</strong> ${t.message}</p>`).join("");
    } else {
      transcriptSection.style.display = "none";
    }

    // Trigger reveal animations after a slight delay to ensure DOM rendering
    setTimeout(() => {
      document.querySelector('.score-section').classList.add('reveal');
      document.querySelector('.badges-container').classList.add('reveal');
      document.getElementById('ai-analysis').classList.add('reveal');
      document.querySelector('.leaderboard').classList.add('reveal');
      document.getElementById('transcript-section').classList.add('reveal');
    }, 100);
  } catch (error) {
    console.error("Fetch final report error:", error);
    finalDiv.innerHTML = `<p class="error">Error fetching final report: ${error.message || "Unknown error. Please try again."}</p>`;
  }
}

function parseAnalysisToPoints(analysis) {
  if (typeof analysis !== 'string') {
    analysis = String(analysis);
  }
  const points = analysis.split('\n').filter(point => point.trim());
  if (points.length === 1 && points[0].startsWith("Error generating AI analysis")) {
    return [points[0]];
  }
  return points.map(point => point.replace(/^-\s*/, '').trim());
}

function getBadgeIcon(badge) {
  const icons = {
    "Code Enthusiast": "🏆",
    "Speedster": "⚡",
    "Communicator": "💬",
    "Team Player": "🤝"
  };
  return icons[badge] || "⭐";
}

function toggleTranscript() {
  const transcriptContent = document.getElementById("transcript-content");
  const toggleButton = document.getElementById("toggle-transcript");
  if (transcriptContent.style.display === "none") {
    transcriptContent.style.display = "block";
    toggleButton.textContent = "Hide";
  } else {
    transcriptContent.style.display = "none";
    toggleButton.textContent = "Show";
  }
}

/*******************************************************
 * 5) Sidebar Toggle
 *******************************************************/
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("collapsed");
}