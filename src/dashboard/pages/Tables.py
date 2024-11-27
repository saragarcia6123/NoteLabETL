import streamlit as st
import requests
import json
import pandas as pd
import request_handler
import os

def main():

    if "response_message" in st.session_state:
        message_type = st.session_state.response_message["type"]
        message = st.session_state.response_message["message"]

        if message_type == "success":
            st.success(message)
        elif message_type == "error":
            st.error(message)

        del st.session_state.response_message

    st.title("Tables")

    #if st.button('New Table'):
        #table_creation_dialog()

    csv = st.file_uploader('Upload from .csv', type=['csv'])
    if csv:
        load_from_csv(csv)

    show_tables()

def load_from_csv(csv):
    df = pd.read_csv(csv)
    create_table(os.path.splitext(csv.name)[0], df)

@st.dialog("New Table")
def table_creation_dialog():
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
        response, status_code = create_table(table_name, st.session_state.df)
        set_response(response, status_code)

def create_table(table_name, df):
    response, status_code = request_handler.create_table(table_name, df.to_dict(orient='records'))
    return response, status_code

def delete_table(table_name):
    response, status_code = request_handler.delete_table(table_name)
    return response, status_code

def show_tables():
    tables_data = request_handler.get_tables()
    if tables_data is None:
        st.error("Failed to fetch tables from server")

    elif len(tables_data) == 0:
        st.write("No tables found")

    else:
        for table_name, table_info in tables_data.items():
            columns = table_info["columns"]
            rows = table_info["rows"]

            df = pd.DataFrame(rows, columns=columns)

            st.subheader(f"Table: {table_name}")
            st.dataframe(df)

            if st.button("Delete table", key=f"delete_{table_name}"):
                response, status_code = delete_table(table_name)
                set_response(response, status_code)

def set_response(response, status_code):
    if status_code == 200:
        st.session_state.response_message = {"type": "success", "message": response}
    else:
        st.session_state.response_message = {"type": "error", "message": response}
    st.rerun()

if __name__ == '__main__':
    main()
