import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, Content
from google.cloud import texttospeech
from transformers import pipeline

# 1. Load environment variables and initialize app
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
VOICE_NAME = "en-IN-Wavenet-D"
LOCATION = "us-east4" # Recommended region for Gemini
app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Required for sessions

# Initialize Google Cloud and Hugging Face clients
# The "us-east4" region is now used for Gemini models
vertexai.init(project=PROJECT_ID, location=LOCATION)
gemini_model = GenerativeModel("gemini-2.5-flash") # The fastest and most cost-effective model
tts_client = texttospeech.TextToSpeechClient()
sentiment_analyzer = pipeline("sentiment-analysis")

@app.route('/')
def index():
    """Renders the main chat interface."""
    # Reset chat history when a new session starts
    session.pop('chat_history', None)
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles user messages, provides empathetic responses, and checks for mood.
    """
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Get sentiment for mood display
    mood_result = sentiment_analyzer(user_message)[0]
    mood = mood_result['label']
    
    # Get the chat history from the session, or start a new chat
    chat_history_dicts = session.get('chat_history', [])
    
    # Reconstruct the ChatSession from the stored history
    chat_history_content = []
    for turn in chat_history_dicts:
        if 'parts' in turn and len(turn['parts']) > 0 and 'text' in turn['parts'][0]:
            chat_history_content.append(Content(parts=[Part.from_text(turn['parts'][0]['text'])], role=turn['role']))

    chat_session = gemini_model.start_chat(history=chat_history_content)
    
    # 1. Get empathetic response from Gemini based on history
    try:
        gemini_response = chat_session.send_message(user_message)
        chatbot_text = gemini_response.text

        # 2. Convert chat history to a JSON-serializable format for the session
        session['chat_history'] = [
            {'role': turn.role, 'parts': [{'text': p.text} for p in turn.parts]}
            for turn in chat_session.history
        ]

    except Exception as e:
        return jsonify({"error": f"Gemini API error: {str(e)}"}), 500
        
    # 3. Convert to speech
    try:
        synthesis_input = texttospeech.SynthesisInput(text=chatbot_text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name=VOICE_NAME,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )
    except Exception as e:
        return jsonify({"error": f"Text-to-Speech API error: {str(e)}"}), 500
    
    # 4. Save audio file
    audio_filename = f"static/chat-audio-{uuid.uuid4()}.mp3"
    with open(audio_filename, "wb") as out:
        out.write(tts_response.audio_content)

    return jsonify({
        "text_response": chatbot_text,
        "audio_url": f"/{audio_filename}",
        "mood": mood
    })

if __name__ == '__main__':
    app.run()