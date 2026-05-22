from streamlit_mic_recorder import mic_recorder

def voice_input():

    audio = mic_recorder(
        start_prompt="🎤 Start",
        stop_prompt="⏹ Stop",
        key='recorder'
    )

    return audio
