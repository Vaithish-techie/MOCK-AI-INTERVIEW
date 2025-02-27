import cv2
import mediapipe as mp
from deepface import DeepFace

# Initialize Face Detection & Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection
face_mesh = mp_face_mesh.FaceMesh()
face_detection = mp_face_detection.FaceDetection()

# Load Video File or Use Webcam
use_webcam = False  # Set to True if you want to use a webcam
video_path = "your_video.mp4"  # Change this to your video file

cap = cv2.VideoCapture(0 if use_webcam else video_path)

frame_skip = 10  # Process every 10th frame
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip frames to reduce load
    
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
    
    # Display the frame (Using cv2.imshow for local)
    cv2.imshow('Facial Analysis', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
