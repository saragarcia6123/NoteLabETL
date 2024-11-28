import streamlit as st
import config

PAGE_TITLE = 'Dashboard'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

def page_dashboard():
    st.title(PAGE_TITLE)

    repo_url = 'https://github.com/saragarcia6123/NoteLabETL'
    st.link_button('Link to GitHub Repository', repo_url)

page_dashboard()