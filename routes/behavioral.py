# routes/behavioral.py
from flask import Blueprint, request, jsonify, session
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
import shutil

behavioral_bp = Blueprint("behavioral", __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create or verify videos folder
VIDEO_STORAGE_DIR = os.path.join(os.getcwd(), "videos")
if not os.path.exists(VIDEO_STORAGE_DIR):
    os.makedirs(VIDEO_STORAGE_DIR)

# Verify FFmpeg is available
ffmpeg_available = False
try:
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_available = True
except (subprocess.CalledProcessError, FileNotFoundError):
    logger.warning("FFmpeg not found in PATH. Audio extraction may fail. Please install FFmpeg and add it to PATH.")

# Initialize MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_pose = mp.solutions.pose  # For gesture analysis
mp_drawing = mp.solutions.drawing_utils

# Function to transcribe using Whisper CLI
def transcribe_audio(audio_path):
    try:
        result = subprocess.run(
            ["whisper", audio_path, "--model", "tiny", "--output_format", "txt"],
            capture_output=True, text=True, check=True
        )
        with open(f"{audio_path}.txt", "r") as f:
            transcript = f.read().strip()
        os.remove(f"{audio_path}.txt")
        return transcript
    except subprocess.CalledProcessError as e:
        logger.error(f"Whisper CLI failed: {e.stderr}")
        raise Exception(f"Transcription failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("Whisper CLI not found. Ensure 'openai-whisper' is installed.")

@behavioral_bp.route("/start_behavioral", methods=["POST"])
def start_behavioral():
    if "behavioral_history" not in session:
        session["behavioral_history"] = []
    if "performance" not in session:
        session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}

    question = "Describe a time you faced a challenge at work. Use the STAR method (Situation, Task, Action, Result) to explain."
    session["behavioral_history"].append({"role": "assistant", "content": question})
    session.modified = True
    return jsonify({"question": question})

@behavioral_bp.route("/submit_behavioral", methods=["POST"])
def submit_behavioral():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    unique_id = int(time.time() * 1000)  # Use timestamp for unique file names
    file_path = os.path.join(VIDEO_STORAGE_DIR, f"behavioral_response_{unique_id}.webm")
    audio_path = os.path.join(VIDEO_STORAGE_DIR, f"behavioral_response_audio_{unique_id}.mp3")
    file.save(file_path)

    try:
        if not ffmpeg_available:
            raise Exception("FFmpeg not available. Please install FFmpeg and add it to PATH.")

        # Extract audio from WebM and save to videos folder
        try:
            stream = ffmpeg.input(file_path)
            stream = ffmpeg.output(stream, audio_path, vn=True, acodec='mp3')
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception(f"Audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")

        # Transcribe with Whisper CLI (voice analysis)
        try:
            transcript = transcribe_audio(audio_path)
            logger.info(f"Voice Analysis - Transcript: {transcript}")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")

        # Tone analysis with Librosa (voice analysis)
        try:
            y, sr = librosa.load(audio_path)
            pitch = librosa.pitch_tune(y, sr)
            energy = librosa.feature.rms(y=y).mean()
            tone = f"Pitch: {pitch.mean():.2f} Hz, Energy: {energy:.4f} (higher energy suggests confidence)"
            logger.info(f"Voice Analysis - Tone: {tone}")
        except Exception as e:
            logger.error(f"Tone analysis error: {str(e)}")
            tone = "Tone analysis failed"

        # Video analysis with MediaPipe (video analysis - body language, gestures)
        try:
            cap = cv2.VideoCapture(file_path)
            eye_contact_frames = 0
            gesture_frames = 0
            total_frames = 0
            with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection, \
                 mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    # Face detection for eye contact
                    results_face = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results_face.detections:
                        eye_contact_frames += 1

                    # Pose detection for gestures (e.g., hand movements)
                    results_pose = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if results_pose.pose_landmarks:
                        landmarks = results_pose.pose_landmarks.landmark
                        left_hand = (landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y)
                        right_hand = (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y)
                        if abs(left_hand[0] - right_hand[0]) > 0.1 or abs(left_hand[1] - right_hand[1]) > 0.1:
                            gesture_frames += 1
                    total_frames += 1
            cap.release()
            body_language = {
                "eye_contact": total_frames > 0 and eye_contact_frames / total_frames > 0.5,
                "gestures": total_frames > 0 and gesture_frames / total_frames > 0.3  # Threshold for active gestures
            }
            logger.info(f"Video Analysis - Body Language: {body_language}")
        except Exception as e:
            logger.error(f"Video analysis error: {str(e)}")
            body_language = {"eye_contact": False, "gestures": False}

        # AI Analysis with Mistral-7B (dynamic feedback)
        system_prompt = (
            "You are a professional behavioral interview assistant. Analyze the user’s response using the STAR method (Situation, Task, Action, Result). "
            "Evaluate clarity, confidence, positivity, and teamwork. Provide feedback in 2-5 bullet points (each starting with '- ') and a follow-up question. "
            "Incorporate speech tone, eye contact, and gestures. If the response is incomplete or unclear, suggest elaboration.\n\n"
            f"User Response: {transcript}\n"
            f"Tone: {tone}\n"
            f"Body Language: Eye contact {'present' if body_language['eye_contact'] else 'absent'}, "
            f"Gestures {'active' if body_language['gestures'] else 'minimal'}\n"
            "Feedback (start each point with '- ') and Follow-up Question:"
        )
        prompt = system_prompt + "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in session["behavioral_history"][-5:]) + "\nAssistant:"
        
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
        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

        feedback_lines = response.split('\n')
        feedback = [line for line in feedback_lines if line.startswith('-')]
        follow_up = next((line for line in feedback_lines[::-1] if not line.startswith('-')), "Can you provide more details about your experience?")

        # Evaluate score based on body language, tone, and content
        score = 0
        if "confidence" in response.lower() or energy > 0.1:  # High energy indicates confidence
            score += 3
        if "teamwork" in response.lower():
            score += 3
        if body_language["eye_contact"]:
            score += 2
        if body_language["gestures"]:
            score += 2
        if len(transcript.split()) > 10:  # Basic length check for clarity
            score += 1
        score = min(10, score)  # Cap at 10

        # Update behavioral traits
        if "confidence" in response.lower():
            session["performance"]["behavioral_traits"].append("Confident")
        if "teamwork" in response.lower():
            session["performance"]["behavioral_traits"].append("Team Player")
        session["behavioral_history"].append({"role": "user", "content": transcript})
        session["behavioral_history"].append({"role": "assistant", "content": f"{'\n'.join(feedback)}\n{follow_up}"})
        session.modified = True

        # Optionally delete files after processing (uncomment to keep files)
        # os.remove(file_path)
        # os.remove(audio_path)

        return jsonify({
            "feedback": feedback,
            "follow_up_question": follow_up,
            "score": score
        })
    except Exception as e:
        logger.error(f"Error in submit_behavioral: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@behavioral_bp.route("/next_behavioral_question", methods=["POST"])
def next_behavioral_question():
    """Provide the next behavioral question dynamically."""
    history = session.get("behavioral_history", [])
    if not history or history[-1]["role"] == "assistant":
        question = "Describe a time you worked in a team to solve a problem. Use the STAR method."
    elif len(history) > 1 and history[-2]["role"] == "user":
        question = "Can you share an example of a difficult decision you made? Use the STAR method."
    else:
        question = "Tell me about a time you failed and what you learned from it. Use the STAR method."
    
    history.append({"role": "assistant", "content": question})
    session["behavioral_history"] = history
    session.modified = True
    return jsonify({"question": question})