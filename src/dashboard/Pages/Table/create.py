import streamlit as st
import app_config
from app.utils import request_handler
from dashboard import message_handler
from utils import pandas_to_sql
import pandas as pd
import os

config = app_config.load()
endpoint_template = config['endpoints']['sqlite']['table']

def page_create_table():
    st.title('New Table')
    message_handler.show_messages()

    options = ["Upload from .csv", "Empty Table"]
    option = st.radio("Select an option", options)

    if option == options[0]:
        upload_from_csv()
    elif option == options[1]:
        new_table()

def upload_from_csv():
    csv = st.file_uploader('Upload from .csv', type=['csv'])
    if csv:
        if st.button('Upload'):
            df = pd.read_csv(csv)
            table_name = os.path.splitext(csv.name)[0]
            columns = pandas_to_sql.columns_from_df(table_name, df)
            rows = pandas_to_sql.rows_from_df(df)

            response, status_code = request_handler.create_table(table_name, columns)
            message_handler.add_response(response, status_code)

            response, status_code = request_handler.insert_rows(table_name, rows)
            message_handler.add_response(response, status_code)

            st.rerun()


def new_table():
    st.title('This section is WIP')

    table_name = st.text_input('Table Name:')

    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=['Column 1'])

    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic")

    if st.button('Create Table'):
        columns = pandas_to_sql.columns_from_df(table_name, st.session_state.df)
        rows = pandas_to_sql.rows_from_df(st.session_state.df)

        response, status_code = request_handler.create_table(table_name, columns)
        message_handler.add_response(response, status_code)

        response, status_code = request_handler.insert_rows(table_name, rows)
        message_handler.add_response(response, status_code)

        st.rerun()

page_create_table()