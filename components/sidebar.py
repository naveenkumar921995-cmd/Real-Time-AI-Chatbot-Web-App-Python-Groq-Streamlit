# ==============================
# components/sidebar.py
# ==============================

import streamlit as st

def sidebar_settings():

    st.sidebar.title("⚙️ Settings")

    model = st.sidebar.selectbox(
        "Choose Model",
        [
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
    )

    temperature = st.sidebar.slider(
        "Temperature",
        0.0,
        1.0,
        0.7
    )

    dark_mode = st.sidebar.toggle("🌙 Dark Mode")

    return model, temperature, dark_mode
