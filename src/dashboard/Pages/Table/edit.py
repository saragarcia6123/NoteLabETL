import streamlit as st
import pandas as pd
import message_handler
from app.utils import request_handler
from src.utils import pandas_to_sql


def page_edit_table():
    st.title('Edit Tables')
    message_handler.show_messages()

    tables = request_handler.get_tables()[0]['tables']
    table_names = list(tables.keys())

    table_name = st.selectbox(
        "Select a Table",
        table_names,
    )

    if table_name:
        st.subheader(f"Table: {table_name}")
        columns = tables[table_name]["columns"]
        rows = tables[table_name]["rows"]
        df = pd.DataFrame(rows, columns=columns)
        df.set_index(df.columns[0], inplace=True)
        edited_df = st.data_editor(df, num_rows='dynamic', use_container_width=True)
        edited_df.reset_index(inplace=True)

        if st.button("Update"):
            rows = pandas_to_sql.rows_from_df(edited_df)
            response, status_code = request_handler.update_rows(table_name, rows)
            message_handler.add_response(response, status_code)
            st.rerun()

page_edit_table()