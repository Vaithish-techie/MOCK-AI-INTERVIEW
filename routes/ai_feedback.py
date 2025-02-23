# routes/ai_feedback.py
from flask import Blueprint, request, jsonify
import openai
import config

ai_feedback_bp = Blueprint("ai_feedback", __name__)

@ai_feedback_bp.route("/analyze_code", methods=["POST"])
def analyze_code():
    data = request.json
    code = data.get("code")
    
    if not code:
        return jsonify({"error": "No code provided"}), 400

    openai.api_key = config.OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[{"role": "system", "content": "Analyze this code for efficiency and readability:\n" + code}]
        )
        analysis = response["choices"][0]["message"]["content"]
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
