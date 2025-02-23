# routes/external_coding.py
import random
from flask import Blueprint, jsonify
from models import CodingQuestion
from extensions import db

external_coding_bp = Blueprint("external_coding", __name__)

@external_coding_bp.route("/balanced_coding_challenges", methods=["GET"])
def balanced_coding_challenges():
    questions = CodingQuestion.query.all()
    if not questions:
        return jsonify({"error": "No coding questions found"}), 404

    # Group by difficulty
    easy = [q for q in questions if q.difficulty.lower() == "easy"]
    medium = [q for q in questions if q.difficulty.lower() == "medium"]
    hard = [q for q in questions if q.difficulty.lower() == "hard"]

    selected = []
    if easy and hard:
        selected.append(random.choice(easy))
        selected.append(random.choice(hard))
    elif easy and medium:
        selected.append(random.choice(easy))
        selected.append(random.choice(medium))
    elif medium and hard:
        selected.append(random.choice(medium))
        selected.append(random.choice(hard))
    elif len(questions) >= 2:
        selected = random.sample(questions, 2)
    else:
        selected = questions  # fallback if <2

    challenges = []
    for q in selected:
        challenges.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "difficulty": q.difficulty,
            "sample_input": q.sample_input or "N/A",
            "sample_output": q.sample_output or "N/A"
        })
    return jsonify({"challenges": challenges})
