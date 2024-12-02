"""
This class is responsible for setting and displaying informative messages,
such as HTTP response messages and status codes.
"""

import streamlit as st

def show_messages():
    if "response_messages" in st.session_state:
        for msg in st.session_state.response_messages:
            message_type = msg["type"]
            message = msg["message"]

            if message_type == "success":
                st.success(message)
            elif message_type == "error":
                st.error(message)

        st.session_state.response_messages.clear()


def add_response(response, status_code):
    if "response_messages" not in st.session_state:
        st.session_state.response_messages = []

    if 200 <= status_code < 300:
        st.session_state.response_messages.append({"type": "success", "message": response})
    else:
        st.session_state.response_messages.append({"type": "error", "message": response})
