import streamlit as st
import config

PAGE_TITLE = 'Tables'
st.set_page_config(page_title=config.PAGE_TITLE.format(PAGE_TITLE), page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import request_handler
import message_handler

def page_tables():
    st.title(PAGE_TITLE)
    message_handler.show_message()

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
                response, status_code = request_handler.delete_table(table_name)
                request_handler.set_response(response, status_code)

page_tables()