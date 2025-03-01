from flask import Flask, Response, jsonify, render_template
from video_processing import process_video
from audio_processing import record_audio
from analysis import analyze_interview
import threading

app = Flask(__name__)

# Global results dictionary
results = {
    "emotion": None,
    "transcription": None,
    "confidence_score": None,
    "analysis_feedback": None
}

@app.route('/')
def index():
    print("Rendering index page...")
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    print("Starting video feed...")
    return Response(process_video(results), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/results')
def get_results():
    print("Analyzing interview results...")
    analyze_interview(results)
    return jsonify(results)

if __name__ == '__main__':
    print("Starting Flask app...")

    # Starting the audio recording thread
    audio_thread = threading.Thread(target=record_audio, args=(results,))
    print("Audio thread starting...")
    audio_thread.start()

    # Starting Flask app with threading enabled
    print("Starting Flask app on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
