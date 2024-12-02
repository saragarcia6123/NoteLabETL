"""
This class is responsible for the streamlit app
"""

import streamlit as st

st.set_page_config(page_title="NoteLab", page_icon=":material/music_note:", layout="wide", initial_sidebar_state="expanded")

pages = {
        "Main": [
            st.Page("Pages/Main/Dashboard.py", title="Dashboard"),
            st.Page("Pages/Main/API Documentation.py", title="API Documentation")
        ],
        "Tables": [
            st.Page("Pages/Table/Tables.py", title="Tables"),
            st.Page("Pages/Table/create.py", title="Create table"),
            st.Page("Pages/Table/edit.py", title="Edit table")
        ]
    }

pg = st.navigation(pages)
pg.run()
