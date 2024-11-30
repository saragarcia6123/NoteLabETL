from flask import Flask, jsonify, request
from flask_restx import Api, Resource
import json
import os
import logging
from src.server.api.sqlite_api import SQLiteAPI

os.makedirs('logs', exist_ok=True)

handler = logging.FileHandler('logs/server.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

def configure_logger(logger):
    logger.setLevel(logging.INFO)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    if not logger.hasHandlers():
        logger.addHandler(handler)


app = Flask(__name__)
configure_logger(app.logger)

flask_api = Api(app)
configure_logger(flask_api.logger)

current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, '../config.json')

with open(config_path) as config_file:
    config = json.load(config_file)

HOST = config['HOST']
FLASK_PORT = int(config['FLASK_PORT'])
DEBUG = config['DEBUG'] == 'True'

FLASK_URL = f"http://{HOST}:{FLASK_PORT}"

current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, '../database/database')

sqlite_api = SQLiteAPI()
sqlite_api.connect(db_path)

if not os.path.exists(db_path):
    print(f"Error: Database file does not exist at {db_path}")
else:
    print(f"Database file found at {db_path}")

@app.route('/swagger.json')
def swagger_json():
    return jsonify(flask_api.__schema__)

class TestResource(Resource):
    def get(self):
        return {"message": "Working!"}, 200

class DatabaseResource(Resource):
    def get(self):
        app.logger.info(f"Fetching tables from {request.url}")
        return sqlite_api.get_tables()

class TableResource(Resource):
    def get(self, table_name):
        app.logger.info(f"Fetching table {table_name} from {request.url}")
        return sqlite_api.get_table(table_name)

    def post(self, table_name):
        app.logger.info(f"Creating table {table_name} from {request.url}")
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        data = request.get_json()
        columns = data.get('columns')
        if not columns:
            return {"error": "No columns provided."}, 400
        try:
            return sqlite_api.create_table(table_name, columns=columns)
        except Exception as e:
            return {"error": str(e)}, 500

    def delete(self, table_name):
        app.logger.info(f"Deleting table {table_name} from {request.url}")
        return sqlite_api.drop_table(table_name)

class TableSchemaResource(Resource):
    def get(self, table_name):
        app.logger.info(f"Fetching schema for table {table_name} from {request.url}")
        return sqlite_api.get_table_schema(table_name)

class RowResource(Resource):
    def get(self, table_name, row_id):
        app.logger.info(f"Fetching row {row_id} from {request.url}")
        return sqlite_api.get_row(table_name, row_id)

class RowsResource(Resource):
    def get(self, table_name):
        app.logger.info(f"Fetching rows from {request.url}")
        conditions = []
        for key, value in request.args.items():
            condition = f"{key}='{value}'"
            conditions.append(condition)
        return sqlite_api.get_rows(table_name, conditions)

    def post(self, table_name):
        app.logger.info(f"Inserting rows into {table_name} from {request.url}")
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        data = request.get_json()["rows"]
        return sqlite_api.insert_rows(table_name, data)

flask_api.add_resource(TestResource, '/test')
flask_api.add_resource(DatabaseResource, '/db/tables')
flask_api.add_resource(TableSchemaResource, '/db/<string:table_name>/schema')
flask_api.add_resource(TableResource, '/db/<string:table_name>')
flask_api.add_resource(RowResource, '/db/<string:table_name>/<int:row_id>')
flask_api.add_resource(RowsResource, '/db/<string:table_name>/rows')

if __name__ == '__main__':
    try:
        print(f"Starting Flask server on {FLASK_URL}...")
        app.run(debug=DEBUG, host=HOST, port=FLASK_PORT)
    finally:
        print("Shutting down Flask server...")
        sqlite_api.disconnect()
