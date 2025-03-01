# routes/chat.py
from flask import Blueprint, request, jsonify, session
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import config
import timeout_decorator
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load the model and tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=config.HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantization_config,
        torch_dtype=torch.float16,
        device_map="auto",
        token=config.HF_TOKEN
    )
    logger.info("Model and tokenizer loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

@chat_bp.route("/clear_conversations", methods=["POST"])
def clear_conversations():
    session.pop("conversation_history_1", None)
    session.pop("conversation_history_2", None)
    session.pop("performance", None)
    logger.info("Conversations cleared from session.")
    return jsonify({"status": "Conversations cleared"}), 200

@chat_bp.route("/message", methods=["POST"])
def chat_message():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    challenge_context = data.get("challenge_context", "")
    code_to_analyze = data.get("code_to_analyze", "")
    challenge_id = data.get("challenge_id", 1)

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
    for msg in session[history_key][-5:]:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
    prompt += "Assistant:"

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.inference_mode():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
        bot_reply = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        bot_reply = bot_reply.replace("<|endoftext|>", "").strip()
    except Exception as e:
        logger.error(f"Error generating message: {str(e)}")
        bot_reply = "Sorry, I couldn’t generate a response due to a technical issue. Let’s continue with the challenge!"

    if context == "Behavioral":
        if "confidence" in bot_reply.lower() or "positive" in bot_reply.lower():
            session["performance"]["behavioral_traits"] = session.get("performance", {}).get("behavioral_traits", []) + ["Confident"]
        if "teamwork" in bot_reply.lower() or "collaboration" in bot_reply.lower():
            session["performance"]["behavioral_traits"] = session.get("performance", {}).get("behavioral_traits", []) + ["Team Player"]
        if "elaborate" in bot_reply.lower() or "clarity" in bot_reply.lower():
            session["behavioral_feedback"] = session.get("behavioral_feedback", []) + [f"Hint provided: {bot_reply}"]

    session[history_key].append({"role": "assistant", "content": bot_reply})
    session.modified = True
    return jsonify({"response": bot_reply})

@chat_bp.route("/analyze_results", methods=["POST"])
def analyze_results():
    logger.info("Received request for /api/analyze_results")
    
    # Extract data from request
    data = request.get_json() or {}
    overall_score = data.get("overall_score", 0)
    category_scores = data.get("category_scores", {})
    time_taken = data.get("time_taken", 0)
    hints_used = data.get("hints_used", 0)
    errors_made = data.get("errors_made", 0)
    behavioral_traits = data.get("behavioral_traits", [])
    transcript_1 = data.get("transcript_1", [])
    transcript_2 = data.get("transcript_2", [])

    logger.debug(f"Request data - Overall Score: {overall_score}, Category Scores: {category_scores}, Time Taken: {time_taken}, Hints Used: {hints_used}, Errors Made: {errors_made}")

    # Fallback analysis (always defined to ensure a response)
    analysis = (
        "- Overall Performance: Your score of {}/30 indicates areas for improvement.\n"
        "- MCQ Performance: You scored {}/10 in MCQs. Consider reviewing fundamental programming concepts to improve your foundational knowledge.\n"
        "- Coding Performance: You scored {}/10 in Coding. Practice more coding challenges, focusing on problem-solving efficiency and code optimization.\n"
        "- Behavioral Performance: You scored {}/10 in Behavioral. Work on articulating your experiences and qualities using the STAR method (Situation, Task, Action, Result).\n"
        "- Time Management: The interview took {} minutes. Aim to balance speed and accuracy to optimize your performance.\n"
        "- Hints and Errors: You used {} hints and made {} errors. Reducing reliance on hints and minimizing errors can boost your confidence.\n"
        "- Recommendations: Dedicate time to consistent practice on platforms like LeetCode or HackerRank, and prepare for behavioral questions by reflecting on past experiences."
    ).format(
        overall_score,
        category_scores.get('MCQs', 0),
        category_scores.get('Coding', 0),
        category_scores.get('Behavioral', 0),
        time_taken,
        hints_used,
        errors_made
    )

    # Attempt AI analysis
    try:
        @timeout_decorator.timeout(15, use_signals=True, timeout_exception=TimeoutError)
        def run_inference():
            logger.debug("Starting AI inference for analyze_results")
            system_prompt = (
                "You are an expert interviewer tasked with analyzing a candidate’s performance in a mock interview. "
                "Based on the performance data provided below, generate a detailed, constructive feedback message in bullet point format. "
                "Each bullet point should address a specific aspect of the candidate’s performance, including overall score, category scores (MCQs, Coding, Behavioral), time taken, hints used, errors made, and behavioral traits. "
                "Identify the candidate’s weak areas and provide specific recommendations for improvement in each area (MCQs, Coding, Behavioral, and overall). "
                "If available, analyze the conversation transcripts to assess the candidate’s approach, problem-solving skills, and communication. "
                "Keep the tone supportive, professional, and encouraging, and format the response as a list of bullet points starting with '- '.\n\n"
                "Performance Data:\n"
                f"- Overall Score: {overall_score}/30\n"
                f"- Category Scores: MCQs: {category_scores.get('MCQs', 0)}/10, Coding: {category_scores.get('Coding', 0)}/10, Behavioral: {category_scores.get('Behavioral', 0)}/10\n"
                f"- Time Taken: {time_taken} minutes\n"
                f"- Hints Used: {hints_used}\n"
                f"- Errors Made: {errors_made}\n"
                f"- Behavioral Traits: {', '.join(behavioral_traits) if behavioral_traits else 'None'}\n"
                f"- Conversation Transcript (Challenge 1):\n{format_transcript(transcript_1)}\n"
                f"- Conversation Transcript (Challenge 2):\n{format_transcript(transcript_2)}\n"
                "Analysis (in bullet points):"
            )

            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            logger.debug(f"Using device: {device}")
            inputs = tokenizer(system_prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
            with torch.inference_mode():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            analysis = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            analysis = analysis.replace("<|endoftext|>", "").strip()

            # Ensure bullet point format
            if not analysis.startswith("- "):
                analysis = "- " + analysis.replace("\n", "\n- ")
            logger.debug(f"AI analysis generated: {analysis}")
            return analysis

        # Run the inference with timeout
        analysis = run_inference()

    except Exception as e:
        logger.error(f"Error in analyze_results: {str(e)}\n{traceback.format_exc()}")
        # Fallback analysis is already defined above, no need to redefine

    # Split the analysis into bullet points and ensure proper formatting
    analysis_points = [point.strip() for point in analysis.split('\n') if point.strip()]
    analysis = '\n'.join(analysis_points)
    logger.info(f"Returning analysis: {analysis}")

    return jsonify({"analysis": analysis})

@chat_bp.route("/evaluate_code_response", methods=["POST"])
def evaluate_code_response():
    logger.info("Received request for /api/evaluate_code_response")
    data = request.get_json() or {}
    bot_response = data.get("bot_response", "")

    # Default score
    score = 4  # Neutral score if AI fails

    try:
        @timeout_decorator.timeout(15, use_signals=True, timeout_exception=TimeoutError)
        def run_inference():
            logger.debug("Starting AI inference for evaluate_code_response")
            system_prompt = (
                "You are an expert coding interviewer. Based on the AI assistant's response to the user's code, evaluate the quality of the user's code. "
                "Provide a score out of 10, where 10 indicates excellent code quality (e.g., correct, efficient, well-structured) and 0 indicates poor quality (e.g., incorrect, inefficient). "
                "Return the score as a single integer.\n\n"
                f"Assistant's Response: {bot_response}\n"
                "Score (0-10):"
            )

            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            inputs = tokenizer(system_prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
            with torch.inference_mode():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_new_tokens=10,
                    do_sample=False,
                    temperature=0.3,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            score = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            score = int(score)
            score = max(0, min(score, 10))
            return score

        score = run_inference()

    except Exception as e:
        logger.error(f"Error in evaluate_code_response: {str(e)}\n{traceback.format_exc()}")
        # Fallback score based on simple keyword analysis
        if "well done" in bot_response.lower() or "correct" in bot_response.lower():
            score = 8
        elif "error" in bot_response.lower() or "incorrect" in bot_response.lower():
            score = 2
        logger.info(f"Fallback score used: {score}")

    return jsonify({"code_score": score})

@chat_bp.route("/adjust_score_for_time", methods=["POST"])
def adjust_score_for_time():
    logger.info("Received request for /api/adjust_score_for_time")
    data = request.get_json() or {}
    current_score = data.get("current_score", 0)
    time_taken = data.get("time_taken", 0)

    adjusted_score = current_score  # Default to current score if AI fails

    try:
        @timeout_decorator.timeout(15, use_signals=True, timeout_exception=TimeoutError)
        def run_inference():
            logger.debug("Starting AI inference for adjust_score_for_time")
            system_prompt = (
                "You are an expert interviewer. Adjust the given score based on the time taken for the interview. "
                "The interview has a time limit of 90 minutes. If the candidate completes the interview faster, award bonus points (up to +2). "
                "If the candidate takes too long, deduct points (up to -2). Return the adjusted score as a single integer.\n\n"
                f"Current Score: {current_score}/10\n"
                f"Time Taken: {time_taken} minutes\n"
                f"Time Limit: 90 minutes\n"
                "Adjusted Score (0-10):"
            )

            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            inputs = tokenizer(system_prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
            with torch.inference_mode():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_new_tokens=10,
                    do_sample=False,
                    temperature=0.3,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            adjusted_score = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            adjusted_score = int(adjusted_score)
            adjusted_score = max(0, min(adjusted_score, 10))
            return adjusted_score

        adjusted_score = run_inference()

    except Exception as e:
        logger.error(f"Error in adjust_score_for_time: {str(e)}\n{traceback.format_exc()}")
        # Fallback adjustment based on time taken
        if time_taken < 30:
            adjusted_score = min(current_score + 2, 10)  # Bonus for fast completion
        elif time_taken > 60:
            adjusted_score = max(current_score - 2, 0)  # Penalty for taking too long
        logger.info(f"Fallback adjusted score used: {adjusted_score}")

    return jsonify({"adjusted_score": adjusted_score})

def format_transcript(transcript):
    if not transcript:
        return "No conversation recorded."
    formatted = ""
    for msg in transcript:
        formatted += f"{msg['role'].capitalize()}: {msg['content']}\n"
    return formatted