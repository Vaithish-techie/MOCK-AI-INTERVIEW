# routes/results.py
from flask import Blueprint, jsonify, session
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

results_bp = Blueprint("results", __name__)

@results_bp.route("/final_report", methods=["GET"])
def final_report():
    # Retrieve scores from session
    mcq_score = session.get("mcq_score", 0)
    behavioral_score = session.get("behavioral_score", 0)
    performance = session.get("performance", {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []})

    logger.info(f"Initial scores - MCQ: {mcq_score}, Behavioral: {behavioral_score}, Performance: {performance}")

    # Calculate Coding score based on AI's feedback
    coding_score = 0
    for i in range(1, 3):
        history_key = f"conversation_history_{i}"
        bot_response = session.get(history_key, [])
        # Find the most recent assistant response related to code execution
        bot_response = next((msg["content"] for msg in reversed(bot_response) if msg["role"] == "assistant" and "code execution result" in msg["content"].lower()), None)
        if bot_response:
            try:
                response = requests.post("http://127.0.0.1:5000/api/evaluate_code_response", json={"bot_response": bot_response})
                response.raise_for_status()
                score = response.json().get("code_score", 0)
                coding_score += score  # Add score for each challenge (out of 10)
                logger.info(f"Coding score for challenge {i}: {score}")
            except requests.RequestException as e:
                logger.error(f"Error evaluating code response for challenge {i}: {str(e)}")
                coding_score += 0

    # Adjust Coding score based on time taken
    try:
        response = requests.post("http://127.0.0.1:5000/api/adjust_score_for_time", json={
            "current_score": coding_score,
            "time_taken": performance["time_taken"]
        })
        response.raise_for_status()
        coding_score = response.json().get("adjusted_score", coding_score)
        logger.info(f"Adjusted coding score: {coding_score}")
    except requests.RequestException as e:
        logger.error(f"Error adjusting score for time: {str(e)}")

    # Ensure coding_score is stored in session
    session["coding_score"] = int(coding_score)
    session.modified = True

    # Calculate overall score
    overall_score = int(mcq_score) + int(coding_score) + int(behavioral_score)
    logger.info(f"Final scores - MCQ: {mcq_score}, Coding: {coding_score}, Behavioral: {behavioral_score}, Overall: {overall_score}")

    # Construct badges array based on performance
    badges = ["Code Enthusiast"]
    if performance["time_taken"] < 30:
        badges.append("Speedster")
    if "Confident" in performance["behavioral_traits"]:
        badges.append("Communicator")
    if "Team Player" in performance["behavioral_traits"]:
        badges.append("Team Player")

    # Prepare performance data for AI analysis
    performance_data = {
        "overall_score": overall_score,
        "category_scores": {
            "MCQs": mcq_score,
            "Coding": coding_score,
            "Behavioral": behavioral_score
        },
        "time_taken": performance["time_taken"],
        "hints_used": performance["hints"],
        "errors_made": performance["errors"],
        "behavioral_traits": performance["behavioral_traits"],
        "transcript_1": session.get("conversation_history_1", []),
        "transcript_2": session.get("conversation_history_2", [])
    }

    # Call AI model to analyze results
    try:
        response = requests.post("http://127.0.0.1:5000/api/analyze_results", json=performance_data)
        response.raise_for_status()
        ai_analysis = response.json().get("analysis", "No AI analysis available.")
    except requests.RequestException as e:
        logger.error(f"Error generating AI analysis: {str(e)}")
        ai_analysis = (
            "- Overall Performance: Your score of {}/30 indicates areas for improvement.\n"
            "- MCQs: You scored {}/10 in MCQs. Review fundamental concepts to improve.\n"
            "- Coding: You scored {}/10 in Coding. Practice coding challenges to enhance your skills.\n"
            "- Behavioral: You scored {}/10 in Behavioral. Prepare to discuss your experiences and qualities.\n"
            "- Time Taken: You took {} minutes. Try to manage your time more effectively.\n"
            "- Recommendations: Focus on strengthening your technical skills and time management."
        ).format(
            overall_score,
            performance_data["category_scores"]["MCQs"],
            performance_data["category_scores"]["Coding"],
            performance_data["category_scores"]["Behavioral"],
            performance_data["time_taken"]
        )

    # Construct transcript
    transcript = []
    for i in range(1, 3):
        history = session.get(f"conversation_history_{i}", [])
        for msg in history:
            transcript.append({"speaker": msg["role"], "message": msg["content"]})

    # Construct the response data
    data = {
        "overall_score": overall_score,
        "time_limit": "90 minutes",
        "category_scores": {
            "MCQs": mcq_score,
            "Coding": coding_score,
            "Behavioral": behavioral_score
        },
        "badges": badges,
        "leaderboard": [
            {"name": "Alice", "totalScore": 25},
            {"name": "Bob", "totalScore": 22},
            {"name": "You", "totalScore": overall_score}
        ],
        "message": ai_analysis,
        "behavioral_feedback": session.get("behavioral_feedback", ["Solid responses overall."]) +
                              [f"Traits observed: {', '.join(performance['behavioral_traits']) if performance['behavioral_traits'] else 'None'}"],
        "transcript": transcript
    }
    return jsonify(data)