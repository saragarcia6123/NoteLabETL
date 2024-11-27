import streamlit as st
import requests
import json
import pandas as pd
import config

def main():
    st.set_page_config(layout="wide")

    cf = config.load()
    SERVER_URL = cf['SERVER_URL']

    st.title("Tables")
    response = requests.get(f"{SERVER_URL}/db/tables")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        st.dataframe(df)
    elif response.status_code == 404:
        st.write("No tables found")
    else:
        st.write("Failed to fetch data from Flask")

if __name__ == '__main__':
    main()
