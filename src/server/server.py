from sqlite3 import OperationalError

from flask import Flask, jsonify, request
from flask_restx import Api, Resource
import sqlite3
import json
import os
import logging
import pandas as pd

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
api = Api(app)

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

if not os.path.exists(db_path):
    print(f"Error: Database file does not exist at {db_path}")
else:
    print(f"Database file found at {db_path}")

@app.route('/swagger.json')
def swagger_json():
    return jsonify(api.__schema__)

class TestResource(Resource):
    def get(self):
        return {"message": "Working!"}, 200

class DatabaseResource(Resource):
    def get(self):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute("VACUUM")

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';")
            tables = cur.fetchall()

            logging.info("Fetched tables: %s", tables)

            if tables and len(tables) > 0:
                tables_data = {}

                for table in tables:
                    table_name = table[0]
                    cur.execute(f"SELECT * FROM {table_name}")
                    rows = cur.fetchall()
                    columns = [description[0] for description in cur.description]

                    tables_data[table_name] = {"columns": columns, "rows": rows}

                response = {"tables": tables_data}
                status_code = 200
            else:
                response = {"tables": {}}
                status_code = 200

            logging.info("Returning data: %s", response)

            return response, status_code

        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            db.close()

class TableResource(Resource):
    def table_exists(self, cur, table_name):
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cur.fetchone() is not None

    def get(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            if not self.table_exists(cur, table_name):
                return {"error": f"Table '{table_name}' not found"}, 404

            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cur.fetchall()]

            result = [dict(zip(columns, row)) for row in rows]

            if not result or len(result) == 0:
                response = {"error": "No results"}
                status_code = 404
            else:
                response = result
                status_code = 200

            return result, status_code

        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            db.close()

    def post(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            data = request.get_json()

            if not data:
                return {'error': 'No data provided'}, 400

            table_name = table_name.replace(' ', '_').lower()

            if self.table_exists(cur, table_name):
                return {"error": f"Table '{table_name}' already exists"}, 404

            df = pd.DataFrame(data)

            try:
                df.to_sql(table_name, db, if_exists='fail', index=False)
                response = {'message': f'Table {table_name} created and data inserted successfully.'}
                status_code = 200
            except OperationalError as e:
                response = {'error': f'Operational error: {str(e)}'}
                status_code = 400

            return response, status_code

        except Exception as e:
            return {'error': str(e)}, 500

        finally:
            db.close()

    def delete(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            if not self.table_exists(cur, table_name):
                return {"error": f"Table '{table_name}' not found"}, 404

            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            db.commit()

            return {"message": f"Table {table_name} dropped successfully!"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

    def put(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            data = request.get_json()
            table_name = table_name.replace(' ', '_').lower()

            if not self.table_exists(cur, table_name):
                return {"error": f"Table '{table_name}' not found"}, 404

            df = pd.DataFrame(data)

            try:
                df.to_sql(table_name, db, if_exists='replace', index=False)
                response = {'message': f'Table {table_name} updated successfully.'}
                status_code = 200
            except OperationalError as e:
                response = {'error': f'Operational error: {str(e)}'}
                status_code = 400

            return response, status_code

        except Exception as e:
            return {'error': str(e)}, 500

        finally:
            db.close()

class TableSchemaResource(Resource):

    def table_exists(self, cur, table_name):
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cur.fetchone() is not None

    def get(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            if not self.table_exists(cur, table_name):
                return {"error": f"Table '{table_name}' not found"}, 404

            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()

            schema = [{"column_name": col[1], "data_type": col[2]} for col in columns]

            return {"table": table_name, "schema": schema}, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

class RowResource(Resource):

    def get(self, table_name, row_id):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cur.fetchall()]

            # Get the row by id
            cur.execute(f"SELECT * FROM {table_name} WHERE id = ?", (row_id,))
            row = cur.fetchone()

            if row:
                result = dict(zip(columns, row))
                return result, 200
            else:
                return {"error": "Row not found"}, 404

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

    def delete(self, table_name, row_id):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
            db.commit()

            if cur.rowcount == 0:
                return {"error": "Row not found"}, 404

            return {"message": f"Row with ID {row_id} deleted successfully!"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

class RowsResource(Resource):
    def post(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400

            columns = list(data.keys())
            values = tuple(data.values())

            placeholders = ", ".join(["?" for _ in columns])

            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            cur.execute(insert_query, values)
            db.commit()

            return {"message": "Row added successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

    def get(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            query_params = request.args.to_dict()

            if not query_params:
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cur.fetchall()]
                result = [dict(zip(columns, row)) for row in rows]
                return result, 200

            where_clause = " AND ".join([f"{key} = ?" for key in query_params])
            values = tuple(query_params.values())

            select_query = f"SELECT * FROM {table_name} WHERE {where_clause}"
            cur.execute(select_query, values)
            rows = cur.fetchall()

            if rows:
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cur.fetchall()]
                result = [dict(zip(columns, row)) for row in rows]
                return result, 200
            else:
                return {"error": "No rows found matching the query"}, 404

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

    def delete(self, table_name):
        try:
            data = request.get_json()
            query_conditions = data.get('query', {})

            if not query_conditions:
                return jsonify({"error": "No query provided"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            query = f"DELETE FROM {table_name} WHERE "
            query_conditions_str = " AND ".join([f"{key} = ?" for key in query_conditions.keys()])
            query += query_conditions_str

            cur.execute(query, tuple(query_conditions.values()))
            db.commit()

            if cur.rowcount == 0:
                return {"error": "No rows matched the query"}, 404

            return {"message": "Rows deleted successfully!"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            db.close()

api.add_resource(TestResource, '/test')
api.add_resource(DatabaseResource, '/db/tables')
api.add_resource(TableSchemaResource, '/db/<string:table_name>/schema')
api.add_resource(TableResource, '/db/<string:table_name>')
api.add_resource(RowResource, '/db/table/<string:table_name>/rows/<string:row_id>')
api.add_resource(RowsResource, '/db/table/<string:table_name>/rows')

if __name__ == '__main__':
    print(f"Starting Flask server on {FLASK_URL}...")
    app.run(debug=DEBUG, host=HOST, port=FLASK_PORT)
