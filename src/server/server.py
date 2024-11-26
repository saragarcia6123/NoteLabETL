from flask import Flask, jsonify, render_template, request
from flask_restx import Api, Resource
import dicttoxml
import sqlite3
import json
import os

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
        return jsonify({"message": "Working!"})

class DatabaseResource(Resource):
    def get(self):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()

            db.close()
            return jsonify({
                "tables": [table[0] for table in tables]
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
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
                return jsonify({"error": f"Table '{table_name}' not found"}), 404

            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cur.fetchall()]

            result = [dict(zip(columns, row)) for row in rows]

            response_type = request.args.get('response_type', 'html')

            if response_type == 'json':
                return jsonify(result)
            elif response_type == 'text':
                return '\n'.join(str(row) for row in result)
            elif response_type == 'html':
                return render_template('index.html', rows=rows)
            elif response_type == 'xml':
                xml_data = dicttoxml.dicttoxml(result)
                return xml_data, 200, {'Content-Type': 'application/xml'}
            else:
                return jsonify({"error": "Invalid response type"}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

    def post(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            if self.table_exists(cur, table_name):
                return jsonify({"error": f"Table '{table_name}' already exists"}), 404

            table_name = table_name.replace(' ', '_').lower()

            columns = data[0].keys()
            values = [list(record.values()) for record in data]

            column_definitions = ", ".join([f"{col.replace(' ', '_')} TEXT" for col in columns])

            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"

            cur.execute(create_table_query)
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
            cur.executemany(insert_query, values)
            db.commit()

            return jsonify({'message': f'Table {table_name} created and data inserted successfully.'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            db.close()

    def delete(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            if not self.table_exists(cur, table_name):
                return jsonify({"error": f"Table '{table_name}' not found"}), 404

            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            db.commit()

            return jsonify({"message": f"Table {table_name} dropped successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
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
                return jsonify({"error": f"Table '{table_name}' not found"}), 404

            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()

            schema = [{"column_name": col[1], "data_type": col[2]} for col in columns]

            return jsonify({"table": table_name, "schema": schema})

        except Exception as e:
            return jsonify({"error": str(e)}), 500
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
                return jsonify(result), 200
            else:
                return jsonify({"error": "Row not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()

    def delete(self, table_name, row_id):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
            db.commit()

            if cur.rowcount == 0:
                return jsonify({"error": "Row not found"}), 404

            return jsonify({"message": f"Row with ID {row_id} deleted successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            db.close()

class RowsResource(Resource):
    def post(self, table_name):
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()

            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            columns = list(data.keys())
            values = tuple(data.values())

            placeholders = ", ".join(["?" for _ in columns])

            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            cur.execute(insert_query, values)
            db.commit()

            return jsonify({"message": "Row added successfully"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
                return jsonify(result), 200

            where_clause = " AND ".join([f"{key} = ?" for key in query_params])
            values = tuple(query_params.values())

            select_query = f"SELECT * FROM {table_name} WHERE {where_clause}"
            cur.execute(select_query, values)
            rows = cur.fetchall()

            if rows:
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cur.fetchall()]
                result = [dict(zip(columns, row)) for row in rows]
                return jsonify(result), 200
            else:
                return jsonify({"error": "No rows found matching the query"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
                return jsonify({"error": "No rows matched the query"}), 404

            return jsonify({"message": "Rows deleted successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
