import csv
import json
import requests
import re

class SQLite_Loader:

    with open('config.json') as config_file:
        config = json.load(config_file)

    FLASK_PORT = int(config['FLASK_PORT'])
    BASE_URL = f"http://{config['HOST']}"
    SERVER_URL = f"{BASE_URL}:{FLASK_PORT}"

    @staticmethod
    def _snake_case(s):
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    @staticmethod
    def load_into_sqlite(csv_file_path, db_path):

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)

            for row in csvreader:
                data = {SQLite_Loader._snake_case(col): val for col, val in zip(header, row)}

                response = requests.post(f"{SQLite_Loader.SERVER_URL}/db/create", json=data)

                if response.status_code == 200:
                    print(f"Successfully added: {data}")
                else:
                    print(f"Failed to add data: {response.status_code}")
