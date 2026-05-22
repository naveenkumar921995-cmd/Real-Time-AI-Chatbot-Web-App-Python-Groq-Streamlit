import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import tempfile
from openai import OpenAI
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
    page_title="🎤 Voice AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ==============================
# LOGIN SYSTEM
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

login()

if not st.session_state.logged_in:
    st.stop()

# ==============================
# SIDEBAR SETTINGS
# ==============================

model, temperature, dark_mode = sidebar_settings()

# ==============================
# DARK MODE
# ==============================

if dark_mode:
    bg_color = "#0E1117"
    text_color = "white"
    chat_bg = "#1E1E1E"
else:
    bg_color = "#FFFFFF"
    text_color = "black"
    chat_bg = "#F1F1F1"

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg_color};
    color: {text_color};
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
st.write("Powered by Groq + Streamlit")

# ==============================
# GROQ CLIENT
# ==============================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=groq_api_key)

# ==============================
# SESSION STATE
# ==============================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_prompt" not in st.session_state:
    st.session_state.voice_prompt = ""

# ==============================
# DISPLAY CHAT HISTORY
# ==============================

for message in st.session_state.messages:

    role = "🧑 You" if message["role"] == "user" else "🤖 AI"

    css_class = (
        "user-chat"
        if message["role"] == "user"
        else "ai-chat"
    )

    st.markdown(
        f"""
        <div class="chat-box {css_class}">
            <b>{role}:</b><br>
            {message["content"]}
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# VOICE ASSISTANT
# ==============================

st.subheader("🎙 Voice Assistant")

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice-recorder"
)

voice_text = None

if audio:

    try:

        # Save audio temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            temp_audio.write(audio["bytes"])

            temp_audio_path = temp_audio.name

        # Groq Whisper Client
        whisper_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        # Speech To Text
        with open(temp_audio_path, "rb") as file:

            transcription = whisper_client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )

        voice_text = transcription.text

        st.success(f"🗣 You Said: {voice_text}")

    except Exception as e:

        st.error(f"Voice Error: {e}")
# ==============================
# TEXT INPUT
# ==============================

text_input = st.chat_input("Type your message...")

# ==============================
# FINAL INPUT
# ==============================

user_input = None

# Text input priority
if text_input:
    user_input = text_input

# Voice button
if st.button("🚀 Send Voice Message"):

    if st.session_state.voice_prompt:

        user_input = st.session_state.voice_prompt

# ==============================
# PROCESS CHAT
# ==============================

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_chat("user", user_input)

    # Show user message
    st.markdown(
        f"""
        <div class="chat-box user-chat">
            <b>🧑 You:</b><br>
            {user_input}
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==============================
    # AI RESPONSE
    # ==============================

    with st.spinner("🤖 AI is thinking..."):

        try:

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
                        <div class="chat-box ai-chat">
                            <b>🤖 AI:</b><br>
                            {full_response}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Save AI message
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
                    lang='en'
                )

                tts.save("response.mp3")

                audio_file = open(
                    "response.mp3",
                    "rb"
                )

                st.audio(
                    audio_file.read(),
                    format="audio/mp3"
                )

            except Exception as audio_error:

                st.warning(
                    f"Voice Output Error: {audio_error}"
                )

        except Exception as e:

            st.error(
                f"AI Error: {e}"
            )

# ==============================
# EXPORT CHAT
# ==============================

export_chat(st.session_state.messages)
