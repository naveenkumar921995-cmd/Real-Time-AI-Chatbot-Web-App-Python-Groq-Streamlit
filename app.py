import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS

# Components
from components.sidebar import sidebar_settings
from components.auth import login
from components.database import save_chat
from components.export_chat import export_chat

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

# =========================
# TITLE
# =========================

st.title("🎤 Voice AI Assistant")

# =========================
# API
# =========================

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)

# =========================
# SESSION
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT
# =========================

for msg in st.session_state.messages:

    role = "🧑 You" if msg["role"] == "user" else "🤖 AI"

    css = (
        "user-chat"
        if msg["role"] == "user"
        else "ai-chat"
    )

    st.markdown(
        f"""
        <div class="chat-box {css}">
            <b>{role}:</b><br>
            {msg["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# TEXT INPUT
# =========================

user_input = st.chat_input(
    "🎤 Use browser voice typing or type here..."
)

# IMPORTANT:
# Use Chrome browser voice typing
# Windows: Win + H
# Mac: Fn key twice

# =========================
# AI CHAT
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
                    <div class="chat-box ai-chat">
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
    # AI VOICE
    # =========================

    try:

        tts = gTTS(full_response)

        tts.save("response.mp3")

        with open("response.mp3", "rb") as audio_file:

            st.audio(
                audio_file.read(),
                format="audio/mp3"
            )

    except Exception as e:

        st.warning(f"Voice Error: {e}")

# =========================
# EXPORT CHAT
# =========================

export_chat(st.session_state.messages)
