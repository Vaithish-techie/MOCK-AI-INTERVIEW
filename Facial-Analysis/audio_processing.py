import whisper
import pyaudio
import wave

# Initialize Whisper Model
whisper_model = whisper.load_model("base")

audio_filename = "live_audio.wav"
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
record_seconds = 10

def record_audio(results):
    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []
    
    print("Recording audio...")
    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("Audio recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the audio file
    wf = wave.open(audio_filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()
    
    # Transcribe the audio
    result = whisper_model.transcribe(audio_filename)
    results["transcription"] = result["text"]
