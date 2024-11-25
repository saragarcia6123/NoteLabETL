from flask import Flask, jsonify, render_template, request
from flask_restx import Api, Resource
import dicttoxml
import sqlite3
import json

app = Flask(__name__)
api = Api(app)

with open('config.json') as config_file:
    config = json.load(config_file)

HOST = config['HOST']
FLASK_PORT = int(config['FLASK_PORT'])
DEBUG = config['DEBUG'] == 'True'

FLASK_URL = f"http://{HOST}:{FLASK_PORT}"

db_path = 'database/database'

with open('secrets.json') as f:
    _secrets = json.load(f)

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
            cur.execute("SELECT name FROM sqlite_master WHERE name!='sqlite_sequence' AND type='table';")
            rows = cur.fetchall()
            db.close()
            return jsonify({"databases": [row[0] for row in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

class TableResource(Resource):
    def get(self):
        try:
            table_name = request.args.get("table_name")
            if not table_name:
                return jsonify({"error": "Table name is required"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cur.fetchall()]
            db.close()

            result = [dict(zip(columns, row)) for row in rows]

            response_type = request.args.get('response_type', 'html')

            if response_type == 'json':
                return jsonify(result)
            elif response_type == 'text':
                return '\n'.join(str(row) for row in result)
            elif response_type == 'html':
                return render_template('billboard_rankings.html', rows=rows)
            elif response_type == 'xml':
                xml_data = dicttoxml.dicttoxml(result)
                return xml_data, 200, {'Content-Type': 'application/xml'}
            else:
                return jsonify({"error": "Invalid response type"}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            table_name = data.get("table_name")
            if not table_name:
                return jsonify({'error': 'Table name is required'}), 400

            table_name = table_name.replace(' ', '_').lower()

            columns = data[0].keys()
            values = [list(record.values()) for record in data]

            column_definitions = ", ".join([f"{col.replace(' ', '_')} TEXT" for col in columns])

            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
            cursor.executemany(insert_query, values)

            conn.commit()
            conn.close()

            return jsonify({'message': f'Table {table_name} created and data inserted successfully.'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    def delete(self):
        try:
            data = request.get_json()
            table_name = data.get("table_name")

            if not table_name:
                return jsonify({"error": "Table name is required"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"DROP TABLE IF EXISTS {table_name}")

            db.commit()
            db.close()

            return jsonify({"message": f"Table {table_name} dropped successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

class TableSchemaResource(Resource):
    def get(self):
        try:
            table_name = request.args.get("table_name")
            if not table_name:
                return jsonify({"error": "Table name is required"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [{"name": col[1], "type": col[2]} for col in cur.fetchall()]
            db.close()

            return jsonify({"schema": columns})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

class RowResource(Resource):
    def get(self):
        try:
            table_name = request.args.get("table_name")
            row_id = request.args.get("id")

            if not table_name or not row_id:
                return jsonify({"error": "Table name and row id are required"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            cur.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cur.fetchall()]

            cur.execute(f"SELECT * FROM {table_name} WHERE id = ?", (row_id,))
            row = cur.fetchone()

            db.close()

            if row:
                result = dict(zip(columns, row))
                return jsonify(result), 200
            else:
                return jsonify({"error": "Row not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def post(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            values = list(data.get("values").values())

            if not table_name or not values:
                return jsonify({"error": "Table name or values missing"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            # Fetch the column names for the specified table dynamically
            cur.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cur.fetchall()]

            # Ensure the number of columns matches number of values in data
            if len(columns) != len(values):
                return jsonify({"error": "Mismatch between columns and data values"}), 400

            # Prepare SQL query dynamically based on columns
            placeholders = ', '.join(['?'] * len(values))
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            cur.execute(sql, values)

            db.commit()
            db.close()

            return jsonify({"message": "Billboard ranking added successfully!"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def put(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            primary_key = data.get("primary_key")
            primary_key_value = data.get("primary_key_value")
            values = data.get("values")

            if not table_name or not primary_key or not primary_key_value or not values:
                return jsonify({"error": "Missing table name, primary key, primary key value or values"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            # Prepare the update query dynamically
            set_clause = ", ".join([f"{col} = ?" for col in values.keys()])
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
            cur.execute(update_query, list(values.values()) + [primary_key_value])

            db.commit()
            db.close()

            return jsonify({"message": "Row updated successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def delete(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            primary_key = data.get("primary_key")
            primary_key_value = data.get("primary_key_value")

            if not table_name or not primary_key or not primary_key_value:
                return jsonify({"error": "Missing table name, primary key or primary key value"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            delete_query = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
            cur.execute(delete_query, (primary_key_value,))

            db.commit()
            db.close()

            return jsonify({"message": "Row deleted successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

class RowsResource(Resource):
    def get(self):
        try:
            table_name = request.args.get("table_name")
            if not table_name:
                return jsonify({"error": "Table name is required"}), 400

            filters = request.args.get("filters", None)  # JSON string of filters
            if filters:
                try:
                    filters = json.loads(filters)  # Parse the filters into a dictionary
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid filter format"}), 400
            else:
                filters = {}

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            # Fetch the column names for the specified table dynamically
            cur.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cur.fetchall()]

            # Build the SQL query with optional filters
            query = f"SELECT * FROM {table_name}"
            if filters:
                where_clause = " AND ".join([f"{col} = ?" for col in filters.keys()])
                query += f" WHERE {where_clause}"

            # Execute query with filter values
            cur.execute(query, tuple(filters.values()))
            rows = cur.fetchall()

            db.close()

            # Return the rows as a list of dictionaries
            result = [dict(zip(columns, row)) for row in rows]

            if result:
                return jsonify(result), 200
            else:
                return jsonify({"error": "No rows found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def post(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            values = data.get("values")  # Dictionary of column-value pairs

            if not table_name or not values:
                return jsonify({"error": "Table name and values are required"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            # Fetch the column names for the specified table dynamically
            cur.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cur.fetchall()]

            # Ensure the number of columns matches the number of values in the data
            if len(columns) != len(values):
                return jsonify({"error": "Mismatch between columns and data values"}), 400

            # Prepare SQL query dynamically based on columns
            placeholders = ', '.join(['?'] * len(values))
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            cur.execute(sql, tuple(values.values()))
            db.commit()
            db.close()

            return jsonify({"message": "Row created successfully!"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def put(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            primary_key = data.get("primary_key")  # The column name of the primary key
            primary_key_value = data.get("primary_key_value")  # Value of the primary key
            values = data.get("values")  # Dictionary of column-value pairs to update

            if not table_name or not primary_key or not primary_key_value or not values:
                return jsonify({"error": "Missing table name, primary key, primary key value, or values"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            # Prepare the update query dynamically
            set_clause = ", ".join([f"{col} = ?" for col in values.keys()])
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
            cur.execute(update_query, tuple(values.values()) + (primary_key_value,))

            db.commit()
            db.close()

            return jsonify({"message": "Row updated successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def delete(self):
        try:
            data = request.get_json()

            table_name = data.get("table_name")
            primary_key = data.get("primary_key")  # The column name of the primary key
            primary_key_value = data.get("primary_key_value")  # Value of the primary key

            if not table_name or not primary_key or not primary_key_value:
                return jsonify({"error": "Missing table name, primary key, or primary key value"}), 400

            db = sqlite3.connect(db_path)
            cur = db.cursor()

            delete_query = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
            cur.execute(delete_query, (primary_key_value,))

            db.commit()
            db.close()

            return jsonify({"message": "Row deleted successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

api.add_resource(TestResource, '/test')
api.add_resource(DatabaseResource, '/db/database')
api.add_resource(TableSchemaResource, '/db/table/schema')
api.add_resource(TableResource, '/db/table')
api.add_resource(RowResource, '/db/table/row')
api.add_resource(RowsResource, '/db/table/rows')

if __name__ == '__main__':
    print(f"Starting Flask server on {FLASK_URL}...")
    app.run(debug=DEBUG, host=HOST, port=FLASK_PORT)
