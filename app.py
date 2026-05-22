import os
import tempfile
import streamlit as st
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# Components
from components.sidebar import sidebar_settings
from components.auth import login
from components.database import save_chat
from components.export_chat import export_chat

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Voice AI Assistant",
    page_icon="🎤",
    layout="wide"
)

# ==============================
# LOGIN
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

login()

if not st.session_state.logged_in:
    st.stop()

# ==============================
# SETTINGS
# ==============================

model, temperature, dark_mode = sidebar_settings()

# ==============================
# THEME
# ==============================

if dark_mode:
    bg = "#0E1117"
    text = "white"
    chat_bg = "#1E1E1E"
else:
    bg = "white"
    text = "black"
    chat_bg = "#F1F1F1"

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg};
    color: {text};
}}

.chat-box {{
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    background-color: {chat_bg};
}}

.user-chat {{
    border-left: 5px solid #4CAF50;
}}

.ai-chat {{
    border-left: 5px solid #2196F3;
}}

</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================

st.title("🎤 Voice AI Assistant")
st.write("Groq + Whisper + Streamlit")

# ==============================
# API CLIENTS
# ==============================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=groq_api_key)

whisper_client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

# ==============================
# SESSION
# ==============================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# DISPLAY CHATS
# ==============================

for msg in st.session_state.messages:

    role = "🧑 You" if msg["role"] == "user" else "🤖 AI"

    css_class = (
        "user-chat"
        if msg["role"] == "user"
        else "ai-chat"
    )

    st.markdown(
        f"""
        <div class="chat-box {css_class}">
            <b>{role}:</b><br>
            {msg["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# VOICE RECORDING
# ==============================

st.subheader("🎙 Voice Assistant")

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice"
)

voice_text = None

# ==============================
# SPEECH TO TEXT
# ==============================

if audio:

    try:

        audio_bytes = audio["bytes"]

        # Save as webm
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".webm"
        ) as temp_audio:

            temp_audio.write(audio_bytes)

            temp_audio_path = temp_audio.name

        # Transcribe using Groq Whisper
        with open(temp_audio_path, "rb") as audio_file:

            transcript = whisper_client.audio.transcriptions.create(
                file=("audio.webm", audio_file, "audio/webm"),
                model="whisper-large-v3",
                response_format="json"
            )

        voice_text = transcript.text

        st.success(f"🗣 You Said: {voice_text}")

    except Exception as e:

        st.error(f"Speech Conversion Error: {e}")

# ==============================
# TEXT INPUT
# ==============================

text_input = st.chat_input("Type your message...")

# ==============================
# FINAL INPUT
# ==============================

user_input = text_input

if voice_text:
    user_input = voice_text

# ==============================
# AI CHAT
# ==============================

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_chat("user", user_input)

    st.markdown(
        f"""
        <div class="chat-box user-chat">
            <b>🧑 You:</b><br>
            {user_input}
        </div>
        """,
        unsafe_allow_html=True
    )

    # AI Response
    with st.spinner("🤖 Thinking..."):

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
                    <div class="chat-box ai-chat">
                        <b>🤖 AI:</b><br>
                        {full_response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

    save_chat("assistant", full_response)

    # ==============================
    # AI VOICE OUTPUT
    # ==============================

    try:

        tts = gTTS(
            text=full_response,
            lang="en"
        )

        tts.save("response.mp3")

        audio_file = open("response.mp3", "rb")

        st.audio(
            audio_file.read(),
            format="audio/mp3"
        )

    except Exception as e:

        st.warning(f"Voice Output Error: {e}")

# ==============================
# EXPORT CHAT
# ==============================

export_chat(st.session_state.messages)
