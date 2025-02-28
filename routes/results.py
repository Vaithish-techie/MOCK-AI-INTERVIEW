from flask import Blueprint, jsonify, session

results_bp = Blueprint("results", __name__)

@results_bp.route("/final_report", methods=["GET"])
def final_report():
    # Retrieve scores from session, default to 0 if not present
    mcq_score = session.get("mcq_score", 0)
    coding_score = session.get("coding_score", 0)
    behavioral_score = session.get("behavioral_score", 0)  # Default to 0 if not set
    performance = session.get("performance", {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []})

    # Calculate overall score
    overall_score = mcq_score + coding_score + behavioral_score

    # Construct badges array, filtering out empty strings
    badges = [
        "Code Enthusiast",
        "Speedster" if performance["time_taken"] < 30 else "",
        "Communicator" if "Confident" in performance["behavioral_traits"] else "",
        "Team Player" if "Team Player" in performance["behavioral_traits"] else ""
    ]
    badges = [badge for badge in badges if badge]  # Filter out empty strings

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
        "message": f"Excellent work! Your total score is {overall_score}/30. Focus on {'fewer hints' if performance['hints'] > 3 else 'speed'} in coding and {'communication' if behavioral_score < 5 else 'nothing'} in behavior.",
        "behavioral_feedback": session.get("behavioral_feedback", ["Solid responses overall."]) + 
                              [f"Traits observed: {', '.join(performance['behavioral_traits']) if performance['behavioral_traits'] else 'None'}"],
        "transcript": []  # Add transcript field (empty list for now)
    }
    return jsonify(data)
