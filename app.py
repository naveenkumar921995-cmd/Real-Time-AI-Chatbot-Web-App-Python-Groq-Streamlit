import streamlit as st
from groq import Groq
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

.stTextInput > div > div > input {
    font-size: 18px;
}

.chat-box {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    color: white;
}

.user-chat {
    background-color: #1f1f1f;
}

.ai-chat {
    background-color: #2b2b2b;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🤖 AI Chatbot")
st.write("Powered by Groq + Streamlit")

# =========================
# API KEY
# =========================
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Please set GROQ_API_KEY in Streamlit Secrets or Environment Variables.")
    st.stop()

# =========================
# GROQ CLIENT
# =========================
client = Groq(api_key=groq_api_key)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:

    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-box user-chat">
                <b>You:</b> {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="chat-box ai-chat">
                <b>AI:</b> {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# USER INPUT
# =========================
user_input = st.chat_input("Type your message...")

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    st.markdown(
        f"""
        <div class="chat-box user-chat">
            <b>You:</b> {user_input}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Generate AI Response
    with st.spinner("Thinking..."):

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        answer = response.choices[0].message.content

    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # Display AI response
    st.markdown(
        f"""
        <div class="chat-box ai-chat">
            <b>AI:</b> {answer}
        </div>
        """,
        unsafe_allow_html=True
    )
