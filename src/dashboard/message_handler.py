import streamlit as st

def show_message():
    if "response_message" in st.session_state:
        message_type = st.session_state.response_message["type"]
        message = st.session_state.response_message["message"]

        if message_type == "success":
            st.success(message)
        elif message_type == "error":
            st.error(message)

        del st.session_state.response_message