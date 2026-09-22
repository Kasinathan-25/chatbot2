import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
from chatbot_config import SYSTEM_PROMPT, BOT_NAME

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)

chat_sessions = {}


@app.route("/")
def index():
    return render_template("index.html", bot_name=BOT_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id") or "default"

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])

    convo = chat_sessions[session_id]

    try:
        response = convo.send_message(user_message)
        reply_text = response.text
    except Exception as e:
        return jsonify({"error": f"Gemini API error: {str(e)}"}), 500

    return jsonify({"reply": reply_text})


@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or "default"
    chat_sessions.pop(session_id, None)
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
