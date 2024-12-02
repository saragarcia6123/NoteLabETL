import logging
from flask import request
from flask_restx import Namespace, Resource, Api
from app.api.sqlite_api import SQLiteAPI
import app_config

config = app_config.load()

root = config['endpoints']['sqlite']['root']
endpoints = config['endpoints']['sqlite']

ns_db = Namespace(name='SQLite', path=root, description='SQLite Database namespace')

logger = logging.getLogger(__name__)

def init_routes(flask_api: Api):
    flask_api.add_namespace(ns_db)

def set_logger(_logger):
    global logger
    logger = _logger

sqlite_api = SQLiteAPI()
db_path = 'src/database/database'
sqlite_api.connect(db_path)


@ns_db.route(endpoints["tables"])
class TablesResource(Resource):
    def get(self):
        logger.info(f"Fetching tables from {request.url}")
        return sqlite_api.get_tables()

@ns_db.route(endpoints["table"])
class TableResource(Resource):
    def get(self, table_name):
        logger.info(f"Fetching table {table_name} from {request.url}")
        return sqlite_api.get_table(table_name)

    def post(self, table_name):
        logger.info(f"Creating table {table_name} from {request.url}")
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
        logger.info(f"Deleting table {table_name} from {request.url}")
        return sqlite_api.drop_table(table_name)

@ns_db.route(endpoints["table_schema"])
class TableSchemaResource(Resource):
    def get(self, table_name):
        logger.info(f"Fetching schema for table {table_name} from {request.url}")
        return sqlite_api.get_table_schema(table_name)

@ns_db.route(endpoints["row"])
class RowResource(Resource):
    def get(self, table_name, row_id):
        logger.info(f"Fetching row {row_id} from {request.url}")
        return sqlite_api.get_row(table_name, row_id)

@ns_db.route(endpoints["rows"])
class RowsResource(Resource):
    def get(self, table_name):
        logger.info(f"Fetching rows from {request.url}")
        conditions = []
        for key, value in request.args.items():
            condition = f"{key}='{value}'"
            conditions.append(condition)
        return sqlite_api.get_rows(table_name, conditions)

    def post(self, table_name):
        logger.info(f"Inserting rows into {table_name} from {request.url}")
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        data = request.get_json()["rows"]
        return sqlite_api.insert_rows(table_name, data)

    def put(self, table_name):
        logger.info(f"Updating rows in {table_name} from {request.url}")
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        data = request.get_json()["rows"]
        return sqlite_api.update_rows(table_name, data)
