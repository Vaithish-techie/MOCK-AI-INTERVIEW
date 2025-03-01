from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load Mistral-7B
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

def analyze_interview(results):
    prompt = f"""
    You are an AI interview coach. Analyze the following data and provide insights:

    - **Facial Expression**: {results["emotion"]}
    - **Speech Transcription**: {results["transcription"]}

    Please provide:
    1. A confidence score from 0 to 100.
    2. Feedback on body language, eye contact, and facial expressions.
    3. Speech analysis (filler words, clarity, speed).

    Return the results in a structured JSON format.
    """

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=300)
    analysis = tokenizer.decode(output[0], skip_special_tokens=True)

    results["analysis_feedback"] = analysis
    results["confidence_score"] = analysis.split("Confidence Score: ")[1].split("\n")[0]  # Extract score
