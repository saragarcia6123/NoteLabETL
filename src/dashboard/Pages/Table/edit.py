import streamlit as st
import config

PAGE_TITLE = 'Edit Table'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import message_handler
import request_handler

def page_edit_table():
    st.title(PAGE_TITLE)
    message_handler.show_message()

    tables = request_handler.get_tables()
    table_names = list(tables.keys())

    table = st.selectbox(
        "Select a Table",
        table_names,
    )

    if table:
        st.subheader(f"Table: {table}")
        columns = tables[table]["columns"]
        rows = tables[table]["rows"]
        df = pd.DataFrame(rows, columns=columns)
        edited_df = st.data_editor(df, num_rows='dynamic', use_container_width=True)

        if st.button("Update Table"):
            response, status_code = request_handler.update_table(table, edited_df)
            request_handler.set_response(response, status_code)

page_edit_table()