# ==============================
# components/voice.py
# ==============================

from streamlit_mic_recorder import mic_recorder

def voice_input():

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key='recorder'
    )

    return audio
