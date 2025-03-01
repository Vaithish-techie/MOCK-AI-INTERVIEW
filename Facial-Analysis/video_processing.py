import cv2
import mediapipe as mp
from deepface import DeepFace

# Initialize Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()

def process_video(results):
    cap = cv2.VideoCapture(0)
    frame_interval = 5  
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face Detection
        results_face = face_detection.process(rgb_frame)
        if results_face.detections:
            for detection in results_face.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, c = frame.shape
                x, y, w, h = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Emotion Analysis
                try:
                    emotion_analysis = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
                    dominant_emotion = emotion_analysis[0]['dominant_emotion']
                    results["emotion"] = dominant_emotion
                    cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                except:
                    pass

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()
