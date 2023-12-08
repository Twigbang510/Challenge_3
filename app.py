from flask import Flask, render_template, request, jsonify
import os
import speech_recognition as sr
from pydub import AudioSegment
from tensorflow.keras.models import load_model
from gtts import gTTS
import playsound

app = Flask(__name__)

# Load pre-trained models
classification_model = load_model("vietnam_model.h5")

def convert_to_wav(input_file, output_file):
    sound = AudioSegment.from_file(input_file)
    sound.export(output_file, format="wav")

def process_voice_file(voice_path):
    # Convert to WAV format
    wav_path = "converted_audio.wav"
    convert_to_wav(voice_path, wav_path)

    # Perform automatic speech recognition (ASR)
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_text = recognizer.recognize_google(source, language="vi-VN")

    # Perform content classification using the loaded model
    prediction = classification_model.predict([[audio_text]])

    return {
        'original_audio_text': audio_text,
        'is_obscene': bool(round(prediction[0][0]))
    }

def speak(text):
    print("Trợ Lý ảo:  ", text)

    tts = gTTS(text=text, lang="vi", slow=False)
    tts.save("sound.mp3")
    playsound.playsound("sound.mp3", True)
    os.remove("sound.mp3")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No voice file provided'})

    voice_file = request.files['file']
    print(voice_file.filename)
    if voice_file.filename == '':
        return jsonify({'error': 'No selected file'})

    try:
        result = process_voice_file(voice_file)
        speak(result['original_audio_text'])  
        return render_template('result.html', result=result)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
