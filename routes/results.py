from flask import Blueprint, jsonify, session, request
import requests
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

results_bp = Blueprint("results", __name__)

@results_bp.route("/final_report", methods=["POST"])
def final_report():
    try:
        # Retrieve data from the request
        data = request.get_json() or {}
        mcq_score = data.get("mcq_score", 0)
        coding_score = data.get("coding_score", 0)  # Raw score out of 20
        behavioral_score = data.get("behavioral_score", 0)
        performance = data.get("performance", {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []})
        transcript_1 = data.get("transcript_1", [])
        transcript_2 = data.get("transcript_2", [])

        # Debug: Log received scores
        logger.info(f"Received scores from frontend - MCQ: {mcq_score}, Coding (out of 20): {coding_score}, Behavioral: {behavioral_score}")

        # Calculate overall score (normalize coding_score from 0-20 to 0-10)
        overall_score = int(mcq_score) + int(coding_score / 2) + int(behavioral_score)
        logger.info(f"Calculated Overall Score: {overall_score}")

        # Construct badges array based on performance
        badges = ["Code Enthusiast"]
        time_taken = performance.get("time_taken", 0)
        if time_taken < 30:
            badges.append("Speedster")
        if "Confident" in performance.get("behavioral_traits", []):
            badges.append("Communicator")
        if "Team Player" in performance.get("behavioral_traits", []):
            badges.append("Team Player")

        # Prepare performance data for AI analysis
        performance_data = {
            "overall_score": overall_score,
            "category_scores": {
                "MCQs": mcq_score,
                "Coding": coding_score,  # Raw score out of 20
                "Behavioral": behavioral_score
            },
            "time_taken": time_taken,
            "hints_used": performance.get("hints", 0),
            "errors_made": performance.get("errors", 0),
            "behavioral_traits": performance.get("behavioral_traits", []),
            "transcript_1": transcript_1,
            "transcript_2": transcript_2
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
                mcq_score,
                coding_score / 2,  # Normalize for display consistency
                behavioral_score,
                time_taken
            )

        # Construct transcript
        transcript = []
        for i in range(1, 3):
            history = transcript_1 if i == 1 else transcript_2
            for msg in history:
                transcript.append({"speaker": msg["role"], "message": msg["content"]})

        # Construct the response data
        data = {
            "overall_score": overall_score,
            "time_limit": "90 minutes",
            "category_scores": {
                "MCQs": mcq_score,
                "Coding": coding_score,  # Raw score out of 20
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
                                  [f"Traits observed: {', '.join(performance.get('behavioral_traits', [])) if performance.get('behavioral_traits', []) else 'None'}"],
            "transcript": transcript
        }
        logger.info(f"Final report generated: {data}")
        return jsonify(data)

    except Exception as e:
        logger.error(f"Error in final_report: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error occurred while generating the final report."}), 500    