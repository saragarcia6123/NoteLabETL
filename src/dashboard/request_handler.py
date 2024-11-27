import requests
import config

cf = config.load()
SERVER_URL = cf['SERVER_URL']

def create_table(table_name, data):
    try:
        response = requests.post(
            f"{SERVER_URL}/db/{table_name}",
            json=data
        )
        response_data = response.json()
        return response_data, response.status_code

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}", 500

def delete_table(table_name):
    try:
        response = requests.delete(
            f"{SERVER_URL}/db/{table_name}"
        )
        response_data = response.json()
        return response_data, response.status_code

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
        return {}
