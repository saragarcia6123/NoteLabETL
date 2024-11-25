import streamlit as st
import json

@st.cache_data
def load():
    with open('config.json') as config_file:
        config = json.load(config_file)

    STREAMLIT_PORT = int(config['STREAMLIT_PORT'])
    FLASK_PORT = int(config['FLASK_PORT'])

    BASE_URL = "http://localhost"
    APP_URL = f"{BASE_URL}:{STREAMLIT_PORT}"
    SERVER_URL = f"{BASE_URL}:{FLASK_PORT}"

    return {
        "STREAMLIT_PORT": STREAMLIT_PORT,
        "FLASK_PORT": FLASK_PORT,
        "BASE_URL": BASE_URL,
        "APP_URL": APP_URL,
        "SERVER_URL": SERVER_URL
    }
