from flask import Blueprint, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Import model and tokenizer from chat.py to reuse
from routes.chat import model, tokenizer

ai_feedback_bp = Blueprint("ai_feedback", __name__)

@ai_feedback_bp.route("/analyze_code", methods=["POST"])
def analyze_code():
    data = request.json
    code = data.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        prompt = (
            "You are an expert coding assistant. Analyze the provided code for correctness, efficiency, style, and potential improvements. "
            "Do not execute the code, but provide detailed feedback including time complexity if applicable. Be clear and concise.\n\n"
            f"Code to Analyze:\n```python\n{code}\n```\n"
        )

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
        with torch.inference_mode():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
        analysis = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": f"Failed to analyze code: {str(e)}"}), 500

@ai_feedback_bp.route("/analyze_results", methods=["POST"])
def analyze_results():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Extract data for analysis
        overall_score = data.get("overall_score", 0)
        category_scores = data.get("category_scores", {})
        mcq_score = category_scores.get("MCQs", 0)
        coding_score = category_scores.get("Coding", 0)  # Raw score out of 20
        behavioral_score = category_scores.get("Behavioral", 0)
        time_taken = data.get("time_taken", 0)
        hints_used = data.get("hints_used", 0)
        errors_made = data.get("errors_made", 0)
        behavioral_traits = data.get("behavioral_traits", [])
        transcript_1 = data.get("transcript_1", [])
        transcript_2 = data.get("transcript_2", [])
        behavioral_transcript = data.get("behavioral_transcript", [])

        # Construct a prompt for Mistral-7B
        prompt = (
            "You are a professional interview performance analyst. Analyze the interview performance data provided and generate a detailed feedback report. "
            "Focus on problem-solving efficiency, coding skills, behavioral performance (using the STAR method), time management, and recommendations for improvement. "
            "Use bullet points for clarity, starting each point with '- '. Include specific scores, traits, and transcript highlights if relevant.\n\n"
            f"Performance Data:\n"
            f"- Overall Score: {overall_score}/30\n"
            f"- MCQs Score: {mcq_score}/10\n"
            f"- Coding Score: {coding_score}/20 (normalized to {coding_score/2}/10 for display)\n"
            f"- Behavioral Score: {behavioral_score}/10\n"
            f"- Time Taken: {time_taken} minutes\n"
            f"- Hints Used: {hints_used}\n"
            f"- Errors Made: {errors_made}\n"
            f"- Behavioral Traits: {', '.join(behavioral_traits) if behavioral_traits else 'None'}\n"
            f"- Transcripts (Coding 1): {', '.join([f'{t.get("role", "Unknown")}: {t.get("content", "")}' for t in transcript_1]) if transcript_1 else 'None'}\n"
            f"- Transcripts (Coding 2): {', '.join([f'{t.get("role", "Unknown")}: {t.get("content", "")}' for t in transcript_2]) if transcript_2 else 'None'}\n"
            f"- Behavioral Transcript: {', '.join([f'{t.get("role", "Unknown")}: {t.get("content", "")}' for t in behavioral_transcript]) if behavioral_transcript else 'None'}\n"
            "Feedback (start each point with '- '):"
        )

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(device)
        with torch.inference_mode():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=500,  # Increased for detailed analysis
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
        analysis = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": f"Failed to analyze results: {str(e)}"}), 500