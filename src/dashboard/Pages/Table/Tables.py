import numpy as np
import streamlit as st
import pandas as pd
import message_handler
from app.utils import request_handler

def page_tables():
    st.title('Tables')
    message_handler.show_messages()

    tables_data = request_handler.get_tables()

    if tables_data is None:
        st.error("Failed to fetch tables from server")

    elif len(tables_data) == 0:
        st.write("No tables found")

    else:
        tables = tables_data[0]['tables']
        for table_name, table_info in tables.items():
            columns = table_info["columns"]
            rows = table_info["rows"]

            df = pd.DataFrame(rows, columns=columns)
            df.replace('NULL', np.nan, inplace=True)

            st.subheader(f"Table: {table_name}")
            st.dataframe(df)

            if st.button("Delete table", key=f"delete_{table_name}"):
                response, status_code = request_handler.drop_table(table_name)
                message_handler.add_response(response, status_code)
                st.rerun()

page_tables()