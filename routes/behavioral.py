from flask import Blueprint, request, jsonify, session
from models import BehavioralQuestion  # Ensure this model is defined in models.py
from extensions import db

behavioral_bp = Blueprint("behavioral", __name__)

SAMPLE_QUESTIONS = [
    {"id": "b1", "question_text": "Tell me about a time you failed and how you overcame it."},
    {"id": "b2", "question_text": "Describe a situation where you had to work in a team. What was your role?"},
    {"id": "b3", "question_text": "How do you handle tight deadlines under pressure?"},
    {"id": "b4", "question_text": "Give an example of when you had to adapt to a major change at work or school."},
    {"id": "b5", "question_text": "How do you ensure clear communication with teammates or stakeholders?"}
]

@behavioral_bp.route("/behavioral_questions", methods=["GET"])
def behavioral_questions():
    try:
        questions = db.session.query(BehavioralQuestion).order_by(db.func.random()).limit(5).all()
    except Exception as e:
        # Optionally log the error: logger.error(f"DB error: {e}")
        questions = []
    if not questions:
        data = SAMPLE_QUESTIONS
    else:
        data = [{"id": q.id, "question": q.question_text} for q in questions]
    
    session["behavioral_questions"] = data
    return jsonify({"questions": data})

@behavioral_bp.route("/submit_behavioral", methods=["POST"])
def submit_behavioral():
    data = request.json
    responses = data.get("responses", [])
    if len(responses) < 5:
        return jsonify({"error": "Please submit responses for at least 5 questions"}), 400

    score = 0
    feedback = []
    for i, resp in enumerate(responses, 1):
        response_text = resp.get("response", "")
        word_count = len(response_text.split())
        if response_text and word_count > 10:
            score += 2
            if "failure" in response_text.lower() or "team" in response_text.lower():
                feedback.append(f"Q{i}: Strong response—shows reflection and teamwork.")
            else:
                feedback.append(f"Q{i}: Good detail, but could emphasize lessons learned.")
        else:
            feedback.append(f"Q{i}: Brief response—please elaborate for better evaluation.")
    
    score = min(score, 10)
    session["behavioral_score"] = score
    session["behavioral_feedback"] = feedback
    return jsonify({"score": score, "message": "Behavioral round completed!", "feedback": feedback})
