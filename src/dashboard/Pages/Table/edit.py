import streamlit as st
import config
import message_handler

PAGE_TITLE = 'Edit Table'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

def page_edit_table():
    st.title(PAGE_TITLE)
    message_handler.show_message()

page_edit_table()