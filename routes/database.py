from flask import Blueprint, jsonify
from models import GeneralQuestion, CodingQuestion
from extensions import db  # Import db from extensions

database_bp = Blueprint("database", __name__)

@database_bp.route("/random_general_question", methods=["GET"])
def get_random_general_question():
    question = db.session.query(GeneralQuestion).order_by(db.func.random()).first()
    if question:
        return jsonify({
            "question": question.question_text,
            "options": [question.option_a, question.option_b, question.option_c, question.option_d],
            "correct_option": question.correct_option
        })
    return jsonify({"error": "No general questions found"}), 404

@database_bp.route("/random_coding_question", methods=["GET"])
def get_random_coding_question():
    question = db.session.query(CodingQuestion).order_by(db.func.random()).first()
    if question:
        return jsonify({
            "title": question.title,
            "description": question.description,
            "difficulty": question.difficulty,
            "sample_input": question.sample_input,
            "sample_output": question.sample_output
        })
    return jsonify({"error": "No coding questions found"}), 404
