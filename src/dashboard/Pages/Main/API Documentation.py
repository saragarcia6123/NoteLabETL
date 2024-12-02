import streamlit as st
from src import app_config

def page_server_api_documentation():
    st.title('API Documentation')

    cf = app_config.load()
    server_url = cf['flask_url']
    swagger_ui_html = f"""
    <iframe src="{server_url}" width="100%" height="600px" frameborder="0"></iframe>
    """

    st.components.v1.html(swagger_ui_html, height=600)

page_server_api_documentation()