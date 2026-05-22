import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import speech_recognition as sr
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
    page_title="Advanced AI Chatbot",
    page_icon="🤖",
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
# SIDEBAR
# =========================

model, temperature, dark_mode = sidebar_settings()

# =========================
# DARK MODE
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

st.title("🤖 Advanced AI Chatbot")

# =========================
# GROQ CLIENT
# =========================

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)

# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "📂 Upload Text File",
    type=["txt"]
)

if uploaded_file:

    file_text = uploaded_file.read().decode("utf-8")

    st.success("File Uploaded Successfully")

    st.text_area(
        "📄 File Content",
        file_text,
        height=200
    )

# =========================
# VOICE INPUT
# =========================

audio_file = st.file_uploader(
    "🎤 Upload Voice File",
    type=["wav"]
)

voice_text = ""

if audio_file:

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:

        temp_audio.write(audio_file.read())

        temp_audio_path = temp_audio.name

    with sr.AudioFile(temp_audio_path) as source:

        audio_data = recognizer.record(source)

        try:
            voice_text = recognizer.recognize_google(audio_data)

            st.success("Voice Converted to Text")

            st.write(voice_text)

        except:
            st.error("Could not recognize voice")

# =========================
# DISPLAY CHAT
# =========================

for message in st.session_state.messages:

    role = "🧑 You" if message["role"] == "user" else "🤖 AI"

    st.markdown(
        f"""
        <div class="chat-box">
        <b>{role}:</b><br>
        {message["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# USER INPUT
# =========================

user_input = st.chat_input("Type your message...")

# Voice input priority
if voice_text:
    user_input = voice_text

# =========================
# AI RESPONSE
# =========================

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_chat("user", user_input)

    with st.spinner("🤖 Thinking..."):

        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=st.session_state.messages,
            stream=True
        )

        full_response = ""

        response_placeholder = st.empty()

        for chunk in response:

            if chunk.choices[0].delta.content:

                full_response += chunk.choices[0].delta.content

                response_placeholder.markdown(
                    f"""
                    <div class="chat-box">
                    <b>🤖 AI:</b><br>
                    {full_response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

    save_chat("assistant", full_response)

# =========================
# EXPORT CHAT
# =========================

export_chat(st.session_state.messages)
