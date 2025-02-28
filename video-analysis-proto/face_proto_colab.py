import cv2
import mediapipe as mp
from deepface import DeepFace
from google.colab.patches import cv2_imshow
import whisper
import wave
import numpy as np
from google.colab import files

# Initialize Whisper Model
model = whisper.load_model("base")

# Initialize Face Detection & Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection
face_mesh = mp_face_mesh.FaceMesh()
face_detection = mp_face_detection.FaceDetection()

# Load Video File Instead of Webcam
video_path = "ok.mp4"  # Change this to your video file
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert frame to RGB (for MediaPipe & DeepFace)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Face Detection
    results = face_detection.process(rgb_frame)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            h, w, c = frame.shape
            x, y, w, h = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)
            
            # Draw Bounding Box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Emotion Analysis
            try:
                emotion_analysis = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = emotion_analysis[0]['dominant_emotion']
                cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            except:
                pass
    
    # Display the frame (Using cv2_imshow for Colab)
    cv2_imshow(frame)
    
# Ask the user to upload an audio file
print("Please upload an audio file for transcription:")
uploaded = files.upload()
audio_file = list(uploaded.keys())[0]  # Get the uploaded filename

# Transcribe Audio with Whisper
result = model.transcribe(audio_file)
print("Transcription:", result["text"])

cap.release()
cv2.destroyAllWindows()
