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
