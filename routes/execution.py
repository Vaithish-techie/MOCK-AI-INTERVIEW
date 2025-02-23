# routes/execution.py
from flask import Blueprint, request, jsonify
import requests
import config

execution_bp = Blueprint("execution", __name__)

@execution_bp.route("/submit_code", methods=["POST"])
def submit_code():
    data = request.json
    source_code = data.get("code")
    language = data.get("language")
    
    if language not in config.LANGUAGE_MAP:
        return jsonify({"error": "Unsupported language"}), 400

    payload = {
        "source_code": source_code,
        "language_id": config.LANGUAGE_MAP[language],
        "stdin": data.get("input", "")
    }

    headers = {
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "X-RapidAPI-Key": config.JUDGE0_API_KEY,
        "Content-Type": "application/json"
    }

    # Append ?wait=true to get the final result in one call
    response = requests.post(f"{config.JUDGE0_BASE_URL}?wait=true", headers=headers, json=payload)
    result = response.json()

    return jsonify({
        "output": result.get("stdout"),
        "error": result.get("stderr"),
        "execution_time": result.get("time")
    })
