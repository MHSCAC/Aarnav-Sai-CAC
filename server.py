import io
import os
import soundfile as sf
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from kokoro_onnx import Kokoro

app = Flask(__name__)
# THIS LINE IS CRITICAL FOR NETLIFY TO TALK TO RENDER:
CORS(app, resources={r"/*": {"origins": "*"}})

print("Loading Kokoro ONNX model...")
kokoro = Kokoro("kokoro-v1.0.int8.onnx", "voices-v1.0.bin")

VOICES = {
    "female": "af_heart",
    "male": "am_adam"
}

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text_to_speak = data.get('text', '')
    selected_gender = data.get('voice', 'male')

    if not text_to_speak:
        return jsonify({'error': 'No text provided'}), 400

    voice_id = VOICES.get(selected_gender, VOICES["male"])

    try:
        samples, sample_rate = kokoro.create(
            text_to_speak, 
            voice=voice_id, 
            speed=1.0, 
            lang="en-us"
        )

        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format='WAV')
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="audio/wav"
        )
    except Exception as e:
        print("Kokoro TTS Error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)