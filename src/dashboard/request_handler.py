import requests
import config
import streamlit as st

cf = config.load()
SERVER_URL = cf['SERVER_URL']

def create_table(table_name, df):
    data = df.to_dict(orient='records')
    try:
        response = requests.post(
            f"{SERVER_URL}/db/{table_name}",
            json=data
        )
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}", 500

def update_table(table_name, df):
    data = df.to_dict(orient='records')
    try:
        response = requests.put(
            f"{SERVER_URL}/db/{table_name}",
            json=data
        )
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}", 500

def delete_table(table_name):
    try:
        response = requests.delete(
            f"{SERVER_URL}/db/{table_name}"
        )
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}", 500

def get_tables():
    response = requests.get(f"{SERVER_URL}/db/tables")
    if response.status_code == 200:
        data = response.json()
        if "tables" in data:
            tables_data = data["tables"]
            return tables_data
        else:
            return {}
    else:
        return None

def set_response(response, status_code):
    if status_code == 200:
        st.session_state.response_message = {"type": "success", "message": response}
    else:
        st.session_state.response_message = {"type": "error", "message": response}
    st.rerun()