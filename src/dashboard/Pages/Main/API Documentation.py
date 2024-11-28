import streamlit as st
import config

PAGE_TITLE = 'API Documentation'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

def page_server_api_documentation():
    st.title(PAGE_TITLE)

    cf = config.load()
    SERVER_URL = cf['SERVER_URL']
    swagger_ui_html = f"""
    <iframe src="{SERVER_URL}" width="100%" height="600px" frameborder="0"></iframe>
    """

    st.components.v1.html(swagger_ui_html, height=600)

page_server_api_documentation()