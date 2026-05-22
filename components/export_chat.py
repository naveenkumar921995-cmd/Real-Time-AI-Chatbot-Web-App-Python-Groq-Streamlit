import streamlit as st

def export_chat(messages):

    chat_text = ""

    for msg in messages:

        chat_text += f"{msg['role']}: {msg['content']}\n"

    st.download_button(
        label="📥 Download Chat",
        data=chat_text,
        file_name="chat.txt",
        mime="text/plain"
    )
