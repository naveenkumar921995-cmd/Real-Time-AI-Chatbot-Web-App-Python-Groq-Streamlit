# ==============================
# components/auth.py
# ==============================

import streamlit as st

def login():

    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

        if username == "admin" and password == "1234":

            st.session_state.logged_in = True
            st.success("Login Successful")

        else:
            st.error("Invalid Credentials")
