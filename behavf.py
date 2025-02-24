import ollama
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import time

app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

# Behavioral Interview Questions
questions = [
    "Tell me about a time you faced a challenge at work. How did you handle it?",
    "Can you describe a situation where you had to work with a difficult colleague?",
    "Give an example of a time you took initiative on a project.",
    "Tell me about a mistake you made and how you fixed it.",
    "How do you handle stress and tight deadlines?"
]

# Folder to store temporary audio files
AUDIO_FOLDER = "audio"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def generate_audio(text, filename):
    """Convert text to speech and save as an audio file."""
    tts = gTTS(text=text, lang='en', slow=False)
    filepath = os.path.join(AUDIO_FOLDER, filename)
    tts.save(filepath)
    return filepath

@app.route("/start", methods=["GET"])
def start():
    # Initial message with the first question
    initial_message = f"Hey there! Ready to dive into this interview? Here’s your first question: {questions[0]}"
    audio_filename = "initial_message.mp3"
    audio_path = generate_audio(initial_message, audio_filename)
    
    # Initialize session variables
    session["question_index"] = 0
    session["waiting_for_response"] = True
    session["audio_counter"] = 0
    
    return jsonify({"reply": initial_message, "audio_url": f"/audio/{audio_filename}"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message.strip():
        return jsonify({"reply": "Hey, I need a bit more to work with—could you give me a response?"})

    # Check session variables
    if "question_index" not in session:
        session["question_index"] = 0
        session["waiting_for_response"] = True
    if "audio_counter" not in session:
        session["audio_counter"] = 0

    question_index = session["question_index"]
    waiting_for_response = session["waiting_for_response"]
    current_question = questions[question_index] if question_index < len(questions) else None

    # Generate a unique audio filename
    audio_counter = session["audio_counter"]
    audio_filename = f"response_{audio_counter}.mp3"
    session["audio_counter"] += 1

    if waiting_for_response:
        # Give feedback on the response
        prompt = f"""
You’re a friendly, experienced interviewer conducting a behavioral interview in real-time. The question I asked was: '{current_question}'. The candidate just said: '{user_message}'. Respond like we’re having a live conversation—keep it professional but warm and engaging. Give specific feedback on what they said, and if it’s vague or short, ask a follow-up question to dig deeper. Avoid robotic phrases like 'good job' or 'well done'—make it feel authentic, like you’re really listening.
"""
        ai_feedback = ollama.chat(
            model='mistral',
            messages=[{"role": "user", "content": prompt}]
        )
        feedback = ai_feedback.get('message', {}).get('content', "Hmm, I’m not quite sure what to make of that—could you tell me more?")
        
        # Generate audio for the feedback
        audio_path = generate_audio(feedback, audio_filename)

        # Switch state
        session["waiting_for_response"] = False
        return jsonify({"reply": feedback, "audio_url": f"/audio/{audio_filename}"})

    else:
        # Ask the next question
        if question_index < len(questions):
            next_question = questions[question_index]
            session["question_index"] += 1
            session["waiting_for_response"] = True
            
            # Generate audio for the next question
            reply = f"Got it, thanks for sharing! Here’s your next question: {next_question}"
            audio_path = generate_audio(reply, audio_filename)

            return jsonify({"reply": reply, "audio_url": f"/audio/{audio_filename}"})
        else:
            # End of interview
            end_message = "That’s it—we’re all done! Thanks for chatting with me!"
            audio_path = generate_audio(end_message, audio_filename)
            return jsonify({"reply": end_message, "audio_url": f"/audio/{audio_filename}"})

@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve the audio file to the frontend."""
    return send_file(os.path.join(AUDIO_FOLDER, filename), mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)