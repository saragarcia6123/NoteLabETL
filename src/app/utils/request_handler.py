"""
This class is responsible for formulating and making requests to the Flask server.
It is used for internal API requests
"""

import requests
from app_config import load

config = load()
flask_url = config['flask_url']
endpoints = config['endpoints']

method_to_request_function_map = {
    'get': requests.get,
    'post': requests.post,
    'delete': requests.delete,
    'put': requests.put,
}

"""Replaces parameter placeholders with the corresponding values"""
def format_endpoint_template(endpoint_template: str, **params) -> str:
    for key, value in params.items():
        placeholder = f"<string:{key}>"
        endpoint_template = endpoint_template.replace(placeholder, value)
    return endpoint_template

"""Makes the request to the server"""
def _make_request(endpoint, method, params=None) -> tuple[dict, int]:
    try:
        request_url = f"{flask_url}{endpoint}"
        request_func = method_to_request_function_map.get(method.lower())
        if not request_func:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response = request_func(url=request_url, json=params)
        response.raise_for_status()
        return response.json(), response.status_code

    except requests.exceptions.RequestException as req_err:
        print(f"Request failed: {req_err}")
        return {"error": str(req_err)}, 500

    except Exception as e:
        print('Error occurred:', e)
        return {"error": str(e)}, 500

sqlite_root = endpoints['sqlite']['root']

"""Requests a list of tables from the SQLite Database"""
def get_tables():
    endpoint = sqlite_root + endpoints['sqlite']['tables']
    method = 'GET'
    return _make_request(endpoint, method)

"""Creates a table's column definitions in the SQLite Database"""
def create_table(table_name, columns):
    endpoint_template = sqlite_root + endpoints['sqlite']['table']
    endpoint = format_endpoint_template(endpoint_template, table_name=table_name)
    method = 'POST'
    params = {'columns': columns}
    return _make_request(endpoint, method, params)

"""Erases a table from the SQLite Database"""
def drop_table(table_name):
    endpoint_template = sqlite_root + endpoints['sqlite']['table']
    endpoint = format_endpoint_template(endpoint_template, table_name=table_name)
    method = 'DELETE'
    return _make_request(endpoint, method)

"""Inserts new rows into an existing table in the SQLite Database"""
def insert_rows(table_name, rows):
    endpoint_template = sqlite_root + endpoints['sqlite']['rows']
    endpoint = format_endpoint_template(endpoint_template, table_name=table_name)
    method = 'POST'
    params = {'rows': rows}
    return _make_request(endpoint, method, params)

"""Updates existing rows in an existing table in the SQLite Database"""
def update_rows(table_name, rows):
    endpoint_template = sqlite_root + endpoints['sqlite']['rows']
    endpoint = format_endpoint_template(endpoint_template, table_name=table_name)
    method = 'PUT'
    params = {'rows': rows}
    return _make_request(endpoint, method, params)