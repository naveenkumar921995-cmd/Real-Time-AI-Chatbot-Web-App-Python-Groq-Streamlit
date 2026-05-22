import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
import tempfile

# Components
from components.sidebar import sidebar_settings
from components.auth import login
from components.database import save_chat
from components.export_chat import export_chat

# =========================
# LOAD ENV
# =========================

load_dotenv()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Voice AI Assistant",
    page_icon="🎤",
    layout="wide"
)

# =========================
# LOGIN
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

login()

if not st.session_state.logged_in:
    st.stop()

# =========================
# SETTINGS
# =========================

model, temperature, dark_mode = sidebar_settings()

# =========================
# THEME
# =========================

if dark_mode:
    bg = "#0E1117"
    text = "white"
else:
    bg = "white"
    text = "black"

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg};
    color: {text};
}}

.chat-box {{
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    background-color: #1E1E1E;
    color: white;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("🎤 Voice AI Assistant")

# =========================
# GROQ CLIENT
# =========================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# CHAT MEMORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHATS
# =========================

for msg in st.session_state.messages:

    role = "🧑 You" if msg["role"] == "user" else "🤖 AI"

    st.markdown(
        f"""
        <div class="chat-box">
        <b>{role}:</b><br>
        {msg["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )

from pydub import AudioSegment
import tempfile
import speech_recognition as sr

# =========================
# LIVE VOICE ASSISTANT
# =========================

from streamlit_mic_recorder import speech_to_text

st.subheader("🎤 Voice Assistant")

voice_text = speech_to_text(
    language='en',
    start_prompt="🎙 Start",
    stop_prompt="⏹ Stop",
    just_once=True,
    use_container_width=True,
    key='STT'
)

if voice_text:

    st.success(f"🗣 You Said: {voice_text}")
# =========================
# WEBM → WAV CONVERSION
# =========================

if audio:

    recognizer = sr.Recognizer()

    audio_bytes = audio["bytes"]

    # Save WEBM
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:

        temp_webm.write(audio_bytes)

        webm_path = temp_webm.name

    # Convert WEBM → WAV
    wav_path = webm_path.replace(".webm", ".wav")

    sound = AudioSegment.from_file(webm_path, format="webm")

    sound.export(wav_path, format="wav")

    try:

        with sr.AudioFile(wav_path) as source:

            audio_data = recognizer.record(source)

            voice_text = recognizer.recognize_google(audio_data)

            st.success(f"🗣 You Said: {voice_text}")

    except Exception as e:

        st.error(f"Speech Recognition Error: {e}")
# =========================
# SPEECH TO TEXT
# =========================

if audio:

    recognizer = sr.Recognizer()

    audio_bytes = audio["bytes"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:

        temp_audio.write(audio_bytes)

        temp_audio_path = temp_audio.name

    try:

        with sr.AudioFile(temp_audio_path) as source:

            audio_data = recognizer.record(source)

            voice_text = recognizer.recognize_google(audio_data)

            st.success(f"🗣 You Said: {voice_text}")

    except Exception as e:

        st.error(f"Speech Recognition Error: {e}")

# =========================
# TEXT INPUT
# =========================

text_input = st.chat_input("Type message...")

user_input = voice_text if voice_text else text_input

# =========================
# AI RESPONSE
# =========================

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_chat("user", user_input)

    with st.spinner("🤖 AI Thinking..."):

        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=st.session_state.messages,
            stream=True
        )

        full_response = ""

        placeholder = st.empty()

        for chunk in response:

            if chunk.choices[0].delta.content:

                full_response += chunk.choices[0].delta.content

                placeholder.markdown(
                    f"""
                    <div class="chat-box">
                    <b>🤖 AI:</b><br>
                    {full_response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Save Response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

    save_chat("assistant", full_response)

    # =========================
    # TEXT TO SPEECH
    # =========================

    tts = gTTS(full_response)

    tts.save("response.mp3")

    audio_file = open("response.mp3", "rb")

    st.audio(audio_file.read(), format="audio/mp3")

# =========================
# EXPORT CHAT
# =========================

export_chat(st.session_state.messages)
