# routes/rounds.py
from flask import Blueprint, request, jsonify, session
from models import GeneralQuestion
from extensions import db
import random
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

rounds_bp = Blueprint("rounds", __name__)

@rounds_bp.route("/get_general_qs", methods=["GET"])
def get_general_qs():
    try:
        count = random.randint(5, 10)
        questions = db.session.query(GeneralQuestion).order_by(db.func.random()).limit(count).all()
        logger.debug(f"Fetched {len(questions)} questions from database")
        if not questions:
            # Seed mock questions into the database
            mock_questions = [
                GeneralQuestion(
                    category="General",
                    question_text="What is 2 + 2?",
                    option_a="3", option_b="4", option_c="5", option_d="6",
                    correct_option="B"
                ),
                GeneralQuestion(
                    category="General",
                    question_text="Which language is known for its use in web development?",
                    option_a="Python", option_b="Java", option_c="JavaScript", option_d="C++",
                    correct_option="C"
                ),
                GeneralQuestion(
                    category="General",
                    question_text="What does HTML stand for?",
                    option_a="Hyper Text Markup Language", option_b="High Tech Markup Language",
                    option_c="Hyper Transfer Markup Language", option_d="None of these",
                    correct_option="A"
                ),
                GeneralQuestion(
                    category="General",
                    question_text="Which data structure uses LIFO?",
                    option_a="Queue", option_b="Stack", option_c="Array", option_d="Linked List",
                    correct_option="B"
                ),
                GeneralQuestion(
                    category="General",
                    question_text="What is the time complexity of binary search?",
                    option_a="O(n)", option_b="O(log n)", option_c="O(n^2)", option_d="O(1)",
                    correct_option="B"
                ),
                GeneralQuestion(
                    category="General",
                    question_text="What is Polymorphism?",
                    option_a="Switching the operating system",
                    option_b="Ability of different classes to be treated as instances of the same class",
                    option_c="Encapsulation of data",
                    option_d="None of the above",
                    correct_option="B"
                )
            ]
            db.session.add_all(mock_questions)
            db.session.commit()
            logger.debug("Seeded mock questions into database")
            questions = db.session.query(GeneralQuestion).order_by(db.func.random()).limit(count).all()

        mcqs = [{"id": str(q.id), "question_text": q.question_text, "options": [q.option_a, q.option_b, q.option_c, q.option_d]} for q in questions]
        session["mcq_questions"] = [{"id": str(q.id), "correct_option": q.correct_option} for q in questions]
        session.modified = True
        logger.debug(f"Session mcq_questions set: {session['mcq_questions']}")
        return jsonify({"mcqs": mcqs})
    except Exception as e:
        logger.error(f"Error in get_general_qs: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}", "total_questions": 0}), 500

@rounds_bp.route("/submit_mcqs", methods=["POST"])
def submit_mcqs():
    data = request.json or {}
    answers = data.get("answers", [])
    logger.debug(f"Received answers: {answers}")

    filtered_answers = [ans for ans in answers if ans.get("selectedOption") is not None]
    logger.debug(f"Filtered answers (non-null selectedOption): {filtered_answers}")

    total_questions = len(session.get("mcq_questions", []))
    logger.debug(f"Total questions in session: {total_questions}")

    if len(filtered_answers) < 5:
        logger.warning(f"Submission failed: Fewer than 5 answers provided. Answered: {len(filtered_answers)}")
        return jsonify({
            "error": "Please submit answers for at least 5 MCQs",
            "total_questions": len(filtered_answers)
        }), 400

    if not total_questions:
        logger.error("No questions found in session")
        return jsonify({"error": "No questions found in session"}), 500

    raw_score = 0
    for ans in filtered_answers:
        q_id = ans.get("id")
        selected = ans.get("selectedOption")
        question = next((q for q in session.get("mcq_questions", []) if q["id"] == q_id), None)
        if question and selected and selected.upper() == question["correct_option"].upper():
            raw_score += 1

    normalized_score = round((raw_score / total_questions) * 10)  # Normalize to a scale of 10
    session["mcq_score"] = normalized_score
    session.modified = True
    logger.debug(f"Submission successful: Raw score: {raw_score}, Normalized score: {normalized_score}")

    return jsonify({
        "round1_score": raw_score,
        "normalized_score": normalized_score,
        "total_questions": total_questions,
        "message": "Round 1 completed!"
    })