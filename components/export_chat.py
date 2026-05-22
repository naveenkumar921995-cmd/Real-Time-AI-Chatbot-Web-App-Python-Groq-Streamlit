# ==============================
# components/export_chat.py
# ==============================

import streamlit as st

def export_chat(messages):

    chat_text = ""

    for msg in messages:

        chat_text += f"{msg['role']}: {msg['content']}\n\n"

    st.download_button(
        label="📥 Download Chat",
        data=chat_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )
