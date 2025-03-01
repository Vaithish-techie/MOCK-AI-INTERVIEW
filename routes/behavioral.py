# routes/behavioral.py
from flask import Blueprint, request, jsonify, session, send_file
import logging
import librosa
import subprocess
import mediapipe as mp
import cv2
import os
import ffmpeg
from routes.chat import model, tokenizer
import torch
import time
from gtts import gTTS  # For Text-to-Speech
from models import BehavioralQuestion  # Import the BehavioralQuestion model
from extensions import db  # Import db for database queries
import traceback

behavioral_bp = Blueprint("behavioral", __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory setup
VIDEO_STORAGE_DIR = os.path.join(os.getcwd(), "videos")
AUDIO_STORAGE_DIR = os.path.join(os.getcwd(), "audio")

for directory in [VIDEO_STORAGE_DIR, AUDIO_STORAGE_DIR]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
        except OSError as e:
            logger.error(f"Failed to create {directory}: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Cannot create {directory}: {str(e)}")

# Dependency checks
ffmpeg_available = False
try:
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_available = True
    logger.debug("FFmpeg is available")
except (subprocess.CalledProcessError, FileNotFoundError):
    logger.error("FFmpeg not found. Install it and add to PATH.")
    raise Exception("FFmpeg not found. Install it and add to PATH.")

try:
    mp_face_detection = mp.solutions.face_detection
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    logger.debug("MediaPipe initialized")
except Exception as e:
    logger.error(f"MediaPipe initialization failed: {str(e)}\n{traceback.format_exc()}")
    raise Exception(f"MediaPipe initialization failed: {str(e)}")

def transcribe_audio(audio_path):
    try:
        result = subprocess.run(
            ["whisper", audio_path, "--model", "tiny", "--output_format", "txt"],
            capture_output=True, text=True, check=True
        )
        transcript_path = f"{audio_path}.txt"
        with open(transcript_path, "r") as f:
            transcript = f.read().strip()
        os.remove(transcript_path)
        logger.debug(f"Transcribed audio: {audio_path}")
        return transcript
    except subprocess.CalledProcessError as e:
        logger.error(f"Whisper failed: {e.stderr}\n{traceback.format_exc()}")
        raise Exception(f"Transcription failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("Whisper CLI not found. Install 'openai-whisper'.")
        raise Exception("Whisper CLI not found. Install 'openai-whisper'.")
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}\n{traceback.format_exc()}")
        raise Exception(f"Transcription failed: {str(e)}")

def generate_audio(question_text, audio_filename):
    try:
        tts = gTTS(text=question_text, lang='en', slow=False)
        audio_path = os.path.join(AUDIO_STORAGE_DIR, f"{audio_filename}.mp3")
        tts.save(audio_path)
        logger.debug(f"Generated audio: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Audio generation failed: {str(e)}\n{traceback.format_exc()}")
        raise Exception(f"Audio generation failed: {str(e)}")

@behavioral_bp.route("/get_audio/<question_id>", methods=["GET"])
def get_audio(question_id):
    audio_path = os.path.join(AUDIO_STORAGE_DIR, f"question_{question_id}.mp3")
    if os.path.exists(audio_path):
        try:
            return send_file(audio_path, mimetype="audio/mpeg", as_attachment=False)
        except Exception as e:
            logger.error(f"Failed to serve audio: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": f"Failed to serve audio: {str(e)}"}), 500
    logger.error(f"Audio not found: {audio_path}")
    return jsonify({"error": "Audio not found"}), 404

@behavioral_bp.route("/start_behavioral", methods=["POST"])
def start_behavioral():
    if "behavioral_history" not in session:
        session["behavioral_history"] = []
    if "performance" not in session:
        session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}
    if "question_count" not in session:
        session["question_count"] = 0

    if session["question_count"] >= 5:
        return jsonify({"error": "Behavioral round completed (5 questions max)."}), 400

    try:
        with db.session.no_autoflush:
            question = BehavioralQuestion.query.order_by(db.func.random()).first()
        question_text = question.question_text if question else "Describe a time you faced a challenge at work. Use the STAR method."
        if not question:
            logger.warning("No questions in database, using default.")

        audio_filename = f"question_{session['question_count']}"
        audio_path = generate_audio(question_text, audio_filename)
        audio_url = f"/api/get_audio/{session['question_count']}"

        session["question_count"] += 1
        session["behavioral_history"].append({"role": "assistant", "content": question_text, "audio_url": audio_url})
        session.modified = True
        logger.debug(f"Started behavioral round with question: {question_text[:100]}...")
        return jsonify({"question": question_text, "audio_url": audio_url})
    except Exception as e:
        logger.error(f"Start behavioral error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Failed to start round: {str(e)}"}), 500

@behavioral_bp.route("/submit_behavioral", methods=["POST"])
def submit_behavioral():
    file = request.files.get('file')
    if not file:
        logger.error("No file provided in request")
        return jsonify({"error": "No file provided"}), 400

    unique_id = int(time.time() * 1000)
    file_path = os.path.join(VIDEO_STORAGE_DIR, f"behavioral_response_{unique_id}.webm")
    audio_path = os.path.join(VIDEO_STORAGE_DIR, f"behavioral_response_audio_{unique_id}.mp3")

    try:
        # Save the file
        file.save(file_path)
        logger.debug(f"File saved: {file_path}")

        # Extract audio
        if not ffmpeg_available:
            raise Exception("FFmpeg not available.")
        try:
            stream = ffmpeg.input(file_path)
            stream = ffmpeg.output(stream, audio_path, vn=True, acodec='mp3')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            logger.debug(f"Audio extracted: {audio_path}")
        except ffmpeg.Error as e:
            raise Exception(f"Audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")

        # Transcribe audio
        transcript = transcribe_audio(audio_path)
        logger.info(f"Transcript: {transcript[:100]}...")

        # Tone analysis
        try:
            y, sr = librosa.load(audio_path)
            pitch = librosa.pitch_tune(y, sr)
            energy = librosa.feature.rms(y=y).mean()
            tone = f"Pitch: {pitch.mean():.2f} Hz, Energy: {energy:.4f}"
            logger.info(f"Tone: {tone}")
        except Exception as e:
            tone = f"Tone analysis failed: {str(e)}"
            logger.error(f"Tone analysis failed: {str(e)}")

        # Video analysis
        try:
            cap = cv2.VideoCapture(file_path)
            eye_contact_frames = gesture_frames = total_frames = 0
            with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection, \
                 mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    total_frames += 1
                    results_face = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results_face.detections:
                        eye_contact_frames += 1
                    results_pose = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results_pose.pose_landmarks:
                        landmarks = results_pose.pose_landmarks.landmark
                        left_hand = (landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y)
                        right_hand = (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y)
                        if abs(left_hand[0] - right_hand[0]) > 0.1 or abs(left_hand[1] - right_hand[1]) > 0.1:
                            gesture_frames += 1
            cap.release()
            body_language = {
                "eye_contact": total_frames > 0 and eye_contact_frames / total_frames > 0.5,
                "gestures": total_frames > 0 and gesture_frames / total_frames > 0.3
            }
            logger.info(f"Body language: {body_language}")
        except Exception as e:
            body_language = {"eye_contact": False, "gestures": False}
            logger.error(f"Video analysis failed: {str(e)}")

        # AI feedback
        try:
            system_prompt = (
                "You are a professional behavioral interview assistant. Analyze the user’s response using the STAR method. "
                f"User Response: {transcript}\nTone: {tone}\nBody Language: Eye contact {'present' if body_language['eye_contact'] else 'absent'}, "
                f"Gestures {'active' if body_language['gestures'] else 'minimal'}\nFeedback (start each point with '- ') and Follow-up Question or Summary:"
            )
            prompt = system_prompt + "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in session["behavioral_history"][-5:]) + "\nAssistant:"
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
            with torch.inference_mode():
                outputs = model.generate(inputs["input_ids"], max_new_tokens=200, do_sample=True, temperature=0.7, top_p=0.9, repetition_penalty=1.1)
            response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            logger.debug(f"AI feedback: {response[:100]}...")
        except Exception as e:
            response = f"AI analysis failed: {str(e)}"
            logger.error(f"AI analysis failed: {str(e)}")

        feedback_lines = response.split('\n')
        feedback = [line for line in feedback_lines if line.startswith('-')]
        follow_up_or_summary = next((line for line in feedback_lines[::-1] if not line.startswith('-')), "Can you provide more details?")

        # Scoring
        score = min(10, sum([
            3 if "confidence" in response.lower() or energy > 0.1 else 0,
            3 if "teamwork" in response.lower() else 0,
            2 if body_language["eye_contact"] else 0,
            2 if body_language["gestures"] else 0,
            1 if len(transcript.split()) > 10 else 0
        ]))

        # Update session
        session["behavioral_score"] = str(int(session.get("behavioral_score", "0")) + score)
        if "confidence" in response.lower():
            session["performance"]["behavioral_traits"].append("Confident")
        if "teamwork" in response.lower():
            session["performance"]["behavioral_traits"].append("Team Player")
        session["behavioral_history"].append({"role": "user", "content": transcript})
        session["behavioral_history"].append({"role": "assistant", "content": f"{'\n'.join(feedback)}\n{follow_up_or_summary}"})
        session.modified = True

        # Next question or summary
        is_final = session["question_count"] >= 5
        next_question = audio_url = None
        if not is_final:
            try:
                with db.session.no_autoflush:
                    next_question_obj = BehavioralQuestion.query.order_by(db.func.random()).first()
                next_question = next_question_obj.question_text if next_question_obj else "Can you provide more details?"
                audio_filename = f"question_{session['question_count']}"
                audio_path = generate_audio(next_question, audio_filename)
                audio_url = f"/api/get_audio/{session['question_count']}"
            except Exception as e:
                logger.error(f"Next question error: {str(e)}")
                next_question = "Can you provide more details?"
        else:
            follow_up_or_summary = "Behavioral round concluded. Thank you!"

        return jsonify({
            "feedback": feedback,
            "follow_up_question": next_question if not is_final else None,
            "summary": follow_up_or_summary if is_final else None,
            "score": score,
            "audio_url": audio_url,
            "is_final": is_final
        })
    except Exception as e:
        logger.error(f"Submit behavioral error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@behavioral_bp.route("/next_behavioral_question", methods=["POST"])
def next_behavioral_question():
    if "question_count" not in session:
        session["question_count"] = 0
    if session["question_count"] >= 5:
        return jsonify({"error": "Behavioral round completed.", "is_final": True}), 400

    try:
        with db.session.no_autoflush:
            question = BehavioralQuestion.query.order_by(db.func.random()).first()
        question_text = question.question_text if question else "Describe a time you worked in a team. Use the STAR method."
        audio_filename = f"question_{session['question_count']}"
        audio_path = generate_audio(question_text, audio_filename)
        audio_url = f"/api/get_audio/{session['question_count']}"

        session["question_count"] += 1
        session["behavioral_history"].append({"role": "assistant", "content": question_text, "audio_url": audio_url})
        session.modified = True
        return jsonify({"question": question_text, "audio_url": audio_url, "is_final": session["question_count"] >= 5})
    except Exception as e:
        logger.error(f"Next question error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Failed to fetch question: {str(e)}"}), 500