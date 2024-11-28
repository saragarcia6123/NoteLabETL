import streamlit as st
import config

PAGE_TITLE = 'Create Table'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

import message_handler
import request_handler
import pandas as pd
import os

def page_create_table():
    st.title(PAGE_TITLE)
    message_handler.show_message()

    options = ["Empty Table", "Upload from .csv"]
    option = st.radio("Select an option", options)

    if option == options[0]:
        new_table()
    elif option == options[1]:
        upload_from_csv()

def upload_from_csv():
    csv = st.file_uploader('Upload from .csv', type=['csv'])
    if csv:
        if st.button('Upload'):
            df = pd.read_csv(csv)
            response, status_code = request_handler.create_table(os.path.splitext(csv.name)[0], df)
            request_handler.set_response(response, status_code)

def new_table():

    table_name = st.text_input('Table Name')

    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()

    if st.button('New Column'):
        new_col_name = f"column_{len(st.session_state.df.columns) + 1}"
        st.session_state.df[new_col_name] = ""

    for i, col in enumerate(st.session_state.df.columns):
        if col != 'index':
            new_col_name = st.text_input(f"Rename column '{col}'", value=col, key=f"col_{i}")
            if new_col_name != col:
                st.session_state.df = st.session_state.df.rename(columns={col: new_col_name})

    st.session_state.df = st.data_editor(st.session_state.df, num_rows='dynamic', use_container_width=True)

    if st.button('Create Table'):
        response, status_code = request_handler.create_table(table_name, st.session_state.df)
        request_handler.set_response(response, status_code)

page_create_table()