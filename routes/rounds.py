# routes/rounds.py
from flask import Blueprint, request, jsonify
from models import GeneralQuestion
from extensions import db
import random

rounds_bp = Blueprint("rounds", __name__)

@rounds_bp.route("/get_general_qs", methods=["GET"])
def get_general_qs():
    # Randomly pick between 5 to 10 questions
    count = random.randint(5, 10)
    questions = db.session.query(GeneralQuestion).order_by(db.func.random()).limit(count).all()
    if not questions:
        return jsonify({"error": "No general questions found"}), 404

    mcqs = []
    for q in questions:
        mcqs.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": [q.option_a, q.option_b, q.option_c, q.option_d],
            "correct_option": q.correct_option  # In production, you may not send the correct answer!
        })
    return jsonify({"mcqs": mcqs})

@rounds_bp.route("/submit_mcqs", methods=["POST"])
def submit_mcqs():
    data = request.json
    answers = data.get("answers", [])
    if len(answers) < 5:
        return jsonify({"error": "Please submit answers for at least 5 MCQs"}), 400

    score = 0
    for ans in answers:
        q_id = ans.get("id")
        selected = ans.get("selectedOption")
        question = db.session.query(GeneralQuestion).get(q_id)
        if question and selected:
            if selected.upper() == question.correct_option.upper():
                score += 1

    return jsonify({"round1_score": score, "message": "Round 1 completed!"})
