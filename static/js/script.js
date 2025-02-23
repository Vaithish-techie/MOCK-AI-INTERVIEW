// script.js

let totalMCQs = 0;
let answeredCount = 0;

// For storing coding challenges fetched from DB
window.codingChallenges = [];

function showScreen(id) {
  const screens = document.querySelectorAll(".screen");
  screens.forEach(screen => screen.classList.remove("active"));
  document.getElementById(id).classList.add("active");

  if (id === "round1") {
    fetchMCQs();
  }
}

function restartInterview() {
  location.reload();
}

// ------------------ ROUND 1: MCQs ------------------
async function fetchMCQs() {
  try {
    const response = await fetch("/api/get_general_qs");
    const data = await response.json();
    const container = document.getElementById("mcq-container");
    const progressLabel = document.getElementById("mcq-progress");
    container.innerHTML = ""; // Clear previous content

    if (data.error) {
      container.innerHTML = `<p class="error">${data.error}</p>`;
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

    // Add change event listeners to all radio buttons
    const allRadios = container.querySelectorAll('input[type="radio"]');
    allRadios.forEach(radio => {
      radio.addEventListener("change", updateAnsweredCount);
    });
  } catch (error) {
    console.error(error);
    document.getElementById("mcq-error").innerText = "Error fetching MCQs";
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
    const data = await response.json();
    if (data.error) {
      document.getElementById("mcq-error").innerText = data.error;
    } else {
      alert(`Round 1 Score: ${data.round1_score}/5`);
      showScreen("round2");
    }
  } catch (error) {
    console.error(error);
    document.getElementById("mcq-error").innerText = "Error submitting MCQs";
  }
}

// ------------------ ROUND 2: Coding Challenge ------------------
// We'll store the two challenges in an array
window.twoChallenges = [];

async function fetchBalancedChallenges() {
  try {
    const resp = await fetch("/api/balanced_coding_challenges");
    const data = await resp.json();
    if (data.error) {
      alert(data.error);
      return;
    }
    const challenges = data.challenges || [];
    if (challenges.length < 2) {
      alert("Could not fetch two challenges.");
      return;
    }
    window.twoChallenges = challenges;
    fillChallenge(1, challenges[0]);
    fillChallenge(2, challenges[1]);
  } catch (error) {
    console.error(error);
    alert("Error fetching challenges");
  }
}

/**
 * Fills the question card for challenge #1 or #2
 */
function fillChallenge(index, challenge) {
  const questionCard = document.getElementById(`question-${index}-card`);
  questionCard.innerHTML = `
    <h3>Problem #${index}: ${challenge.title} (${challenge.difficulty})</h3>
    <p>${challenge.description}</p>
    <p><strong>Sample Input:</strong> ${challenge.sample_input}</p>
    <p><strong>Sample Output:</strong> ${challenge.sample_output}</p>
  `;
}

/**
 * Runs code for challenge #1 or #2
 */
async function runCode(index) {
  const codeInput = document.getElementById(`code-input-${index}`);
  const langSelect = document.getElementById(`language-select-${index}`);
  const outputBlock = document.getElementById(`output-block-${index}`);
  const resultDiv = document.getElementById(`execution-result-${index}`);

  const code = codeInput.value;
  const language = langSelect.value;

  try {
    const response = await fetch("/api/submit_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language })
    });
    const data = await response.json();
    // Show the output block
    outputBlock.style.display = "block";
    resultDiv.innerHTML = `
      <p><strong>Output:</strong> ${data.output || "No output"}</p>
      <p><strong>Error:</strong> ${data.error || "No error"}</p>
      <p><strong>Execution Time:</strong> ${data.execution_time || "N/A"}</p>
    `;
  } catch (error) {
    console.error(error);
    outputBlock.style.display = "block";
    resultDiv.innerHTML = `<p class="error">Error executing code</p>`;
  }
}

/**
 * Toggles AI analysis for challenge #1 or #2
 * and calls /api/analyze_code with the code from the editor
 */
async function toggleAnalysis(index) {
  const analysisBlock = document.getElementById(`analysis-block-${index}`);
  const analysisResult = document.getElementById(`analysis-result-${index}`);
  const codeInput = document.getElementById(`code-input-${index}`).value;

  // If hidden, show it and do the AI call
  const isVisible = (analysisBlock.style.display === "block");
  if (!isVisible) {
    analysisBlock.style.display = "block";
    // call AI
    try {
      const response = await fetch("/api/analyze_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeInput })
      });
      const data = await response.json();
      if (data.error) {
        analysisResult.innerHTML = `<p class="error">${data.error}</p>`;
      } else {
        analysisResult.innerHTML = `<p><strong>Analysis:</strong> ${data.analysis}</p>`;
      }
    } catch (error) {
      console.error(error);
      analysisResult.innerHTML = `<p class="error">Error analyzing code</p>`;
    }
  } else {
    // Hide it if already visible
    analysisBlock.style.display = "none";
  }
}

// ------------------ FINAL REPORT ------------------
async function fetchFinalReport() {
  try {
    const response = await fetch("/api/final_report");
    const data = await response.json();
    const finalDiv = document.getElementById("final-report");

    if (data.error) {
      finalDiv.innerHTML = `<p class="error">${data.error}</p>`;
      return;
    }
    finalDiv.innerHTML = `
      <p><strong>Overall Score:</strong> ${data.overall_score}/10</p>
      <p><strong>Time Limit:</strong> ${data.time_limit}</p>
      <h3>Category Scores</h3>
      <ul>
        ${Object.entries(data.category_scores).map(([cat, val]) => `<li><strong>${cat}:</strong> ${val}</li>`).join("")}
      </ul>
      <p><strong>Feedback:</strong> ${data.feedback}</p>
      <h4>Transcript</h4>
      <div>
        ${data.transcript.map(t => `<p><strong>${t.speaker}:</strong> ${t.message}</p>`).join("")}
      </div>
    `;
  } catch (error) {
    console.error(error);
    document.getElementById("final-report").innerText = "Error fetching final report";
  }
}
