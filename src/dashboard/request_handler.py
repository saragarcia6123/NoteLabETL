from typing import Type, Union
import requests
import config
import streamlit as st
import pandas as pd
import pandas.api.types as ptypes
import logging
import re
import os
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Float

cf = config.load()
SERVER_URL = cf['SERVER_URL']

logger = logging.getLogger('request_handler_logger')
logger.setLevel(logging.INFO)
os.makedirs('logs', exist_ok=True)
handler = logging.FileHandler('logs/request_handler.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def infer_sql_type(dtype) -> Type[Union[Integer, DateTime, String, Float]]:
    type_mapping = {
        'integer': Integer,
        'datetime64': DateTime,
        'string': String,
        'bool': Integer,
        'float': Float,
        'object': String
    }
    for pdt, sqt in type_mapping.items():
        check = getattr(ptypes, f'is_{pdt}_dtype')
        if check(dtype):
            return sqt
    return String

def to_snake_case(name: str) -> str:
    name = re.sub(r'\s+', '_', name)
    return re.sub(r'[^\w_]', '', name).lower()

def create_table_from_df(table_name: str, df: pd.DataFrame) -> tuple[str, int]:
    try:
        metadata = MetaData()

        columns = [
            Column(to_snake_case(col), infer_sql_type(df[col].dtype))
            for col in df.columns
        ]

        table = Table(table_name, metadata, *columns)

        columns_with_types = [
            f"{col.name} {str(col.type)}" for col in table.columns
        ]

        logger.info(f"Schema created: {columns_with_types}")

        # Create table
        params = {"columns": columns_with_types}
        response = requests.post(
            f"{SERVER_URL}/db/{table_name}",
            json=params
        )
        response.raise_for_status()

        # Insert rows
        if not df.empty:
            rows = df.values.tolist()  # Convert DataFrame rows to list of lists (only values)
            insert_params = {"rows": rows}
            insert_response = requests.post(
                f"{SERVER_URL}/db/{table_name}/rows",
                json=insert_params
            )
            insert_response.raise_for_status()

            logger.info("Table created and data inserted successfully.")
            return insert_response.json(), insert_response.status_code

        else:
            logger.info("Table created successfully.")
            return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return str(e), 500

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

def drop_table(table_name):
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
        logger.info(f"Retrieved tables from server.")
        if "tables" in data:
            tables_data = data["tables"]
            return tables_data
        else:
            return {}
    else:
        return None

def set_response(response, status_code):
    if 200 <= status_code < 300:
        st.session_state.response_message = {"type": "success", "message": response}
    else:
        st.session_state.response_message = {"type": "error", "message": response}
    st.rerun()