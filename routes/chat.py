from flask import Blueprint, request, jsonify, session
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import config

chat_bp = Blueprint("chat", __name__)

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Define model and tokenizer at the module level for reuse
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=config.HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantization_config,
        torch_dtype=torch.float16,
        device_map="auto",
        token=config.HF_TOKEN
    )
except Exception as e:
    print(f"Error loading model: {e}")
    raise

@chat_bp.route("/clear_conversations", methods=["POST"])
def clear_conversations():
    session.pop("conversation_history_1", None)
    session.pop("conversation_history_2", None)
    session.pop("performance", None)
    return jsonify({"status": "Conversations cleared"}), 200

@chat_bp.route("/message", methods=["POST"])
def chat_message():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    challenge_context = data.get("challenge_context", "")
    code_to_analyze = data.get("code_to_analyze", "")
    challenge_id = data.get("challenge_id", 1)  # Default to 1 if not provided

    # Use separate conversation histories for each challenge
    history_key = f"conversation_history_{challenge_id}"
    if history_key not in session:
        session[history_key] = []
    if "performance" not in session:
        session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}

    if not user_message and not code_to_analyze:
        return jsonify({"response": "Hey, let’s get started! What do you want to do?"})

    session[history_key].append({"role": "user", "content": user_message if user_message else "(Code analysis requested)"})
    context = "Technical"
    if "Behavioral:" in user_message:
        context = "Behavioral"
        user_message = user_message.replace("Behavioral: ", "")
    elif code_to_analyze:
        context = "CodeAnalysis"

    if context == "Technical":
        system_prompt = (
            "You are a professional coding interview assistant acting as an interviewer. Your role is to guide the user through the coding challenge specified in the 'Current Challenge' below. "
            "Focus strictly on the challenge provided in the 'Current Challenge' context and do not introduce or discuss other challenges. "
            "Provide clear, concise answers to user queries, offer hints if asked, and solve coding challenges with explanations when requested. "
            "Always ask follow-up questions to engage the user (e.g., 'Would you like a hint?', 'How would you approach this?', 'Would you like to optimize this further?'). "
            "If the user says something unrelated (e.g., greetings like 'hi'), respond politely and steer them back to the challenge. "
            "Maintain an encouraging tone and act as a mentor, helping the user succeed in the challenge.\n\n"
            f"Current Challenge: {challenge_context}\n"
        )
    elif context == "CodeAnalysis":
        system_prompt = (
            "You are an expert coding assistant. Analyze the provided code for correctness, efficiency, style, and potential improvements. "
            "Do not execute the code, but provide detailed feedback including time complexity if applicable. Be clear and concise.\n\n"
            f"Code to Analyze:\n```python\n{code_to_analyze}\n```\n"
        )
    else:  # Behavioral
        system_prompt = (
            "You are a professional behavioral interview assistant. Analyze responses for clarity, confidence, positivity, and teamwork, "
            "offering feedback or hints (e.g., 'Can you elaborate on your action?'). Use the STAR method (Situation, Task, Action, Result) to evaluate. "
            "Keep it supportive, concise, and professional!\n\n"
        )

    prompt = system_prompt
    for msg in session[history_key]:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
    prompt += "Assistant:"

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
    bot_reply = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    bot_reply = bot_reply.replace("<|endoftext|>", "").strip()

    if context == "Behavioral":
        if "confidence" in bot_reply.lower() or "positive" in bot_reply.lower():
            session["performance"]["behavioral_traits"] = session.get("performance", {}).get("behavioral_traits", []) + ["Confident"]
        if "teamwork" in bot_reply.lower() or "collaboration" in bot_reply.lower():
            session["performance"]["behavioral_traits"] = session.get("performance", {}).get("behavioral_traits", []) + ["Team Player"]
        if "elaborate" in bot_reply.lower() or "clarity" in bot_reply.lower():
            session["behavioral_feedback"] = session.get("behavioral_feedback", []) + [f"Hint provided: {bot_reply}"]

    session[history_key].append({"role": "assistant", "content": bot_reply})
    return jsonify({"response": bot_reply})
