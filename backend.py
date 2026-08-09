import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_DIR = Path("data")
PREFERENCES_FILE = DATA_DIR / "accessibility_preferences.json"
FEEDBACK_FILE = DATA_DIR / "accpyessibility_feedback.jsonl"
DEFAULT_PREFERENCES = {
    "highContrast": False,
    "fontSize": 16,
    "screenReaderEnabled": False,
    "reduceMotion": False,
    "colorScheme": "light",
    "textSpacing": "normal",
    "voiceGuidance": False,
}

DATA_DIR.mkdir(exist_ok=True)


def load_preferences():
    if not PREFERENCES_FILE.exists():
        save_preferences(DEFAULT_PREFERENCES)

    with PREFERENCES_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_preferences(preferences):
    with PREFERENCES_FILE.open("w", encoding="utf-8") as handle:
        json.dump(preferences, handle, indent=2)
    return preferences


def validate_preferences(data):
    preferences = load_preferences()

    if "highContrast" in data:
        preferences["highContrast"] = bool(data["highContrast"])

    if "fontSize" in data:
        try:
            font_size = int(data["fontSize"])
            preferences["fontSize"] = max(10, min(48, font_size))
        except (TypeError, ValueError):
            pass

    if "screenReaderEnabled" in data:
        preferences["screenReaderEnabled"] = bool(data["screenReaderEnabled"])

    if "reduceMotion" in data:
        preferences["reduceMotion"] = bool(data["reduceMotion"])

    if "colorScheme" in data and data["colorScheme"] in ["light", "dark", "sepia"]:
        preferences["colorScheme"] = data["colorScheme"]

    if "textSpacing" in data and data["textSpacing"] in ["normal", "wide", "extra-wide"]:
        preferences["textSpacing"] = data["textSpacing"]

    if "voiceGuidance" in data:
        preferences["voiceGuidance"] = bool(data["voiceGuidance"])

    return preferences


def describe_image(image_url: str) -> str:
    return (
        "This image description is a placeholder. "
        "For production, integrate a vision API or upload analysis service." 
        f"Requested URL: {image_url}"
    )


def speak_text(text: str, voice: str = "default") -> str:
    if shutil.which("say"):
        command = ["say"]
        if voice != "default":
            command.extend(["-v", voice])
        command.append(text)

        try:
            subprocess.Popen(command)
            return "Speech synthesis started using macOS built-in voice engine."
        except Exception as error:
            return f"Unable to start speech synthesis: {error}"

    return "TTS not available. Install a local speech engine or integrate cloud speech APIs."


@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "accessibility-backend"})


@app.route("/api/accessibility/preferences", methods=["GET"])
def get_preferences():
    return jsonify(load_preferences())


@app.route("/api/accessibility/preferences", methods=["POST"])
def update_preferences():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    preferences = validate_preferences(data)
    save_preferences(preferences)
    return jsonify(preferences)


@app.route("/api/accessibility/describe", methods=["POST"])
def describe():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    image_url = data.get("imageUrl")
    if not image_url:
        return jsonify({"error": "Missing imageUrl."}), 400

    alt_text = describe_image(image_url)
    return jsonify({"imageUrl": image_url, "altText": alt_text})


@app.route("/api/accessibility/read", methods=["POST"])
def read_text():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Missing or invalid text."}), 400

    voice = data.get("voice", "default")
    result = speak_text(text.strip(), voice)
    return jsonify({"text": text.strip(), "voice": voice, "message": result})


@app.route("/api/accessibility/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    message = data.get("message", "")
    category = data.get("category", "general")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Missing or invalid message."}), 400

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "category": category,
        "message": message.strip(),
    }

    with FEEDBACK_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")

    return jsonify({"saved": True, "entry": entry}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
