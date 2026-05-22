# ==============================
# app.py
# ==============================

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Components
from components.sidebar import sidebar_settings
from components.voice import voice_input
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
    page_title="Advanced AI Chatbot",
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
# DARK/LIGHT MODE
# ==============================

if dark_mode:
    bg_color = "#0E1117"
    text_color = "white"
    chat_bg = "#1E1E1E"
else:
    bg_color = "white"
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

st.title("🤖 Advanced AI Chatbot")
st.write("Powered by Groq + Streamlit")

# ==============================
# GROQ API
# ==============================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Groq API Key not found")
    st.stop()

client = Groq(api_key=groq_api_key)

# ==============================
# SESSION MEMORY
# ==============================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# FILE UPLOAD
# ==============================

uploaded_file = st.file_uploader(
    "📂 Upload File",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

# ==============================
# VOICE INPUT
# ==============================

voice = voice_input()

# ==============================
# DISPLAY CHAT HISTORY
# ==============================

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-box user-chat">
                <b>🧑 You:</b><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-box ai-chat">
                <b>🤖 AI:</b><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# ==============================
# USER INPUT
# ==============================

user_input = st.chat_input("Type your message...")

# ==============================
# PROCESS CHAT
# ==============================

if user_input:

    # Save User Message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    save_chat("user", user_input)

    # Display User Message
    st.markdown(
        f"""
        <div class="chat-box user-chat">
            <b>🧑 You:</b><br>
            {user_input}
        </div>
        """,
        unsafe_allow_html=True
    )

    # AI Streaming Response
    with st.spinner("🤖 AI is typing..."):

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

    # Save AI Response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

    save_chat("assistant", full_response)

# ==============================
# EXPORT CHAT
# ==============================

export_chat(st.session_state.messages)
