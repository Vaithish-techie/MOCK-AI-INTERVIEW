# routes/rounds.py
from flask import Blueprint, request, jsonify, session
from models import GeneralQuestion
from extensions import db
import random

rounds_bp = Blueprint("rounds", __name__)

@rounds_bp.route("/get_general_qs", methods=["GET"])
def get_general_qs():
    try:
        count = random.randint(5, 10)
        questions = db.session.query(GeneralQuestion).order_by(db.func.random()).limit(count).all()
        if not questions:
            mock_questions = [
                {"id": str(i), "question_text": f"Sample Question {i}?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_option": "A"}
                for i in range(1, count + 1)
            ]
            session["mcq_questions"] = [{"id": str(i), "correct_option": "A"} for i in range(1, count + 1)]
            return jsonify({"mcqs": mock_questions})
        mcqs = [{"id": str(q.id), "question_text": q.question_text, "options": [q.option_a, q.option_b, q.option_c, q.option_d]} for q in questions]
        session["mcq_questions"] = [{"id": str(q.id), "correct_option": q.correct_option} for q in questions]
        return jsonify({"mcqs": mcqs})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}", "total_questions": 0}), 500

@rounds_bp.route("/submit_mcqs", methods=["POST"])
def submit_mcqs():
    data = request.json
    answers = data.get("answers", [])
    total_questions = len(answers)  # Calculate total questions

    if total_questions < 5:
        return jsonify({
            "error": "Please submit answers for at least 5 MCQs",
            "total_questions": total_questions
        }), 400

    raw_score = 0
    for ans in answers:
        q_id = ans.get("id")
        selected = ans.get("selectedOption")
        question = next((q for q in session.get("mcq_questions", []) if q["id"] == q_id), None)
        if question and selected and selected.upper() == question["correct_option"].upper():
            raw_score += 1

    # Normalize the score to be out of 10
    normalized_score = round((raw_score / total_questions) * 10)  # Normalize to a scale of 10
    session["mcq_score"] = normalized_score

    return jsonify({
        "round1_score": raw_score,  # Raw score for UI display
        "normalized_score": normalized_score,  # Normalized score for overall calculation
        "total_questions": total_questions,  # Total number of questions
        "message": "Round 1 completed!"
    })