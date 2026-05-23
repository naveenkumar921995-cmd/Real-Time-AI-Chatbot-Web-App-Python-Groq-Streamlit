# ==============================
# app.py
# ==============================

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

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
    page_title="Advanced AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
# CUSTOM THEMES
# ==============================

if dark_mode:

    bg_color = "#0E1117"
    text_color = "white"
    card_color = "#1E1E1E"
    border_color = "#333333"

else:

    bg_color = "#F5F7FA"
    text_color = "#000000"
    card_color = "#FFFFFF"
    border_color = "#DDDDDD"

# ==============================
# CUSTOM CSS
# ==============================

st.markdown(f"""
<style>

html, body, [class*="css"] {{
    font-family: 'Segoe UI', sans-serif;
}}

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

.main-title {{
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 5px;
}}

.sub-title {{
    color: gray;
    margin-bottom: 20px;
}}

.chat-container {{
    padding-bottom: 120px;
}}

.chat-box {{
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 14px;
    background-color: {card_color};
    border: 1px solid {border_color};
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}

.user-chat {{
    border-left: 6px solid #4CAF50;
}}

.ai-chat {{
    border-left: 6px solid #2196F3;
}}

.chat-role {{
    font-weight: bold;
    margin-bottom: 8px;
    font-size: 17px;
}}

.timestamp {{
    font-size: 12px;
    color: gray;
    margin-top: 8px;
}}

.stChatInputContainer {{
    bottom: 15px;
}}

</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================

st.markdown(
    '<div class="main-title">🤖 Advanced AI Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Powered by Groq + Streamlit</div>',
    unsafe_allow_html=True
)

# ==============================
# GROQ API
# ==============================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:

    st.error("❌ GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=groq_api_key)

# ==============================
# SESSION STATES
# ==============================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "typing" not in st.session_state:
    st.session_state.typing = False

# ==============================
# TOP ACTION BUTTONS
# ==============================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []
        st.rerun()

with col2:

    export_chat(st.session_state.messages)

with col3:

    st.download_button(
        label="📥 Export JSON",
        data=str(st.session_state.messages),
        file_name="chat_backup.json",
        mime="application/json"
    )

# ==============================
# FILE UPLOAD
# ==============================

uploaded_file = st.file_uploader(
    "📂 Upload Text File",
    type=["txt", "md", "py", "csv"]
)

file_content = ""

if uploaded_file:

    try:

        file_content = uploaded_file.read().decode("utf-8")

        with st.expander("📄 Uploaded File Preview"):

            st.text(file_content[:5000])

    except Exception as e:

        st.error(f"File Error: {e}")

# ==============================
# CHAT HISTORY
# ==============================

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:

    role = "🧑 You" if message["role"] == "user" else "🤖 AI"

    css_class = (
        "user-chat"
        if message["role"] == "user"
        else "ai-chat"
    )

    timestamp = message.get(
        "time",
        datetime.now().strftime("%H:%M")
    )

    st.markdown(
        f"""
        <div class="chat-box {css_class}">
            <div class="chat-role">{role}</div>
            <div>{message["content"]}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# CHAT INPUT
# ==============================

user_input = st.chat_input(
    "Type your message here..."
)

# ==============================
# APPEND FILE CONTENT
# ==============================

if user_input and file_content:

    user_input += f"\n\nUploaded File Content:\n{file_content[:4000]}"

# ==============================
# PROCESS CHAT
# ==============================

if user_input:

    current_time = datetime.now().strftime("%H:%M")

    # Save User Message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": current_time
    })

    save_chat("user", user_input)

    # Display User Message
    st.markdown(
        f"""
        <div class="chat-box user-chat">
            <div class="chat-role">🧑 You</div>
            <div>{user_input}</div>
            <div class="timestamp">{current_time}</div>
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
                messages=[
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ],
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
                            <div class="chat-role">🤖 AI</div>
                            <div>{full_response}▌</div>
                            <div class="timestamp">
                                {datetime.now().strftime("%H:%M")}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Final Response Render
            response_placeholder.markdown(
                f"""
                <div class="chat-box ai-chat">
                    <div class="chat-role">🤖 AI</div>
                    <div>{full_response}</div>
                    <div class="timestamp">
                        {datetime.now().strftime("%H:%M")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Save AI Message
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "time": datetime.now().strftime("%H:%M")
            })

            save_chat("assistant", full_response)

        except Exception as e:

            st.error(f"AI Error: {e}")
