"""
This class is responsible for formulating and executing SQL queries to the SQLite Database
"""

import sqlite3
import logging
import os
import re
from typing import Optional, List, Dict, Any, Tuple

class SQLiteAPI:

    # Ensure consistency across log messages
    MESSAGES = {
        "SQLITE_VERSION": "SQLite version: {sqlite_version}",

        "SQLITE_INITIALIZING": "Initializing SQLiteAPI instance...",
        "SQLITE_INITIALIZED": "SQLiteAPI instance initialized.",

        "SQLITE_DISCONNECTING": "Disconnecting from SQLiteAPI instance...",
        "SQLITE_DISCONNECTED": "SQLiteAPI instance disconnected.",

        "INITIALIZING_CONNECTION": "Initializing connection to database {db_name}...",
        "TERMINATING_CONNECTION": "Terminating connection to database {db_name}...",

        "ALREADY_CONNECTED": "Already connected to database {db_name}.",
        "NOT_CONNECTED": "Not connected to a database.",

        "CONNECT_SUCCESS": "Successfully connected to database {db_name}.",
        "CONNECT_FAIL": "Failed to connect to database {db_name}.",

        "DISCONNECT_SUCCESS": "Database {db_name} connection closed.",
        "DISCONNECT_FAIL": "Failed to close database connection {db_name}.",

        "DB_EXISTS": "Database '{db_name}' already exists.",

        "TABLE_EXISTS": "Table '{table_name}' already exists.",
        "TABLE_FOUND": "Table '{table_name}' found.",
        "TABLE_NOT_FOUND": "Table '{table_name}' not found.",

        "NO_TABLES_FOUND": "No tables found in database '{db_name}'.",

        "TABLE_CREATED": "Table '{table_name}' created successfully.",
        "TABLE_CREATION_FAIL": "Failed to create table '{table_name}'.",

        "TABLE_DELETED": "Table '{table_name}' deleted successfully.",
        "TABLE_DELETION_FAIL": "Failed to delete table '{table_name}'.",

        "TABLE_INSERTED": "Row inserted into table '{table_name}'.",
        "TABLE_INSERTION_FAIL": "Failed to insert row into table '{table_name}'.",

        "TABLE_UPDATED": "Table '{table_name}' updated successfully.",
        "TABLE_UPDATE_FAIL": "Failed to update table '{table_name}'.",

        "TABLE_RETRIEVED": "Successfully retrieved rows from table '{table_name}'.",
        "TABLE_SCHEMA_RETRIEVED": "Successfully retrieved schema of table '{table_name}'.",

        "ROWS_FOUND": "Row(s) found in table '{table_name}'.",
        "ROWS_NOT_FOUND": "Row(s) not found in table '{table_name}'.",

        "ROWS_RETRIEVED": "Successfully retrieved rows from table '{table_name}'.",
        "ROWS_RETRIEVAL_FAIL": "Failed to retrieve rows from table '{table_name}'.",

        "ROWS_INSERTED": "Row(s) inserted into table '{table_name}'.",
        "ROWS_INSERTION_SUCCESS": "Row(s) inserted into table '{table_name}'.",
        "ROWS_INSERTION_FAIL": "Failed to insert row(s) into table '{table_name}'.",

        "ROWS_UPDATE_SUCCESS": "Row(s) updated in table '{table_name}'.",
        "ROWS_UPDATE_FAIL": "Failed to update row(s) in table '{table_name}'.",

        "ROWS_DELETED": "Row(s) deleted from table '{table_name}'.",
        "ROWS_DELETION_FAIL": "Failed to delete row(s) from table '{table_name}'.",

        "INVALID_ROWS": "Invalid row data for table '{table_name}'.",

        "DB_PATH_NOT_FOUND": "Database path {db_path} not found.",
        "INVALID_TABLE_NAME": "Invalid table name '{table_name}'."
    }

    valid_name_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
    valid_path_pattern = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9 ._-]*[a-zA-Z0-9])?\.[a-zA-Z0-9_-]+$')

    def __init__(self):
        self.logger = logging.getLogger('sqlite_api_logger')
        self.logger.setLevel(logging.INFO)
        os.makedirs('logs', exist_ok=True)
        self.handler = logging.FileHandler('logs/sqlite_api.log')
        self.handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        self.logger.info(self.MESSAGES["SQLITE_INITIALIZING"])
        self.logger.info(self.MESSAGES["SQLITE_VERSION"].format(sqlite_version=sqlite3.sqlite_version_info))

        self.db_path: Optional[str] = None
        self.db_name: Optional[str] = None
        self.db: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connected: bool = False

    def __del__(self):
        self.disconnect()
        self.logger.info(self.MESSAGES["SQLITE_DISCONNECTED"])

    def __enter__(self):
        self.logger.info(self.MESSAGES["SQLITE_INITIALIZED"])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        self.logger.info(self.MESSAGES["SQLITE_DISCONNECTED"])

    @staticmethod
    def to_snake_case(name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def verify_name(self, name: str) -> bool:
        return self.valid_name_pattern.match(name) is not None

    """
    Connect to SQLite Database
    Parameters:
        db_path (str) - The path to the database file
        force_connect (bool) - Whether to force a connection if already connected
    Returns:
        Response message (str)
        HTTP Status Code (int)
    """
    def connect(self, db_path:str, force_connect:bool=False) -> Tuple[str, int]:

        self.logger.info(self.MESSAGES["INITIALIZING_CONNECTION"].format(db_name=db_path))
        db_name = os.path.basename(db_path).split('.')[0]

        try:
            db_name = self.to_snake_case(db_name)
            if not self.verify_name(db_name):
                message = self.MESSAGES["INVALID_DB_NAME"].format(db_name=db_name)
                self.logger.error(message)
                return message, 400

            db_path = db_path.strip()
            if not os.path.exists(db_path):
                message = self.MESSAGES["DB_PATH_NOT_FOUND"].format(db_path=db_path)
                self.logger.error(message)
                return message, 404

            if self.connected:
                message = self.MESSAGES["ALREADY_CONNECTED"].format(db_name=self.db_name)
                self.logger.warning(message)
                if force_connect:
                    self.logger.info(f"Force connecting to database {db_name}...")
                    self.disconnect()
                else:
                    return message, 409

            self.db_path = db_path
            self.db_name = db_name
            self.db = sqlite3.connect(db_path, check_same_thread=False)
            self.cursor = self.db.cursor()
            self.connected = True

            message = self.MESSAGES["CONNECT_SUCCESS"].format(db_name=self.db_name)
            self.logger.info(message)
            return message, 200

        except Exception as e:
            self.db = None
            self.db_path = None
            self.db_name = None
            self.cursor = None
            self.connected = False
            message = f"{self.MESSAGES['CONNECT_FAIL'].format(db_name=db_name)}: {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Disconnect from SQLite Database
    Parameters:
        force_disconnect (bool) - Whether to force a disconnect if not connected
    Returns:
        Response message (str)
        HTTP Status Code (int)
    """
    def disconnect(self, force_disconnect:bool=False) -> Tuple[str, int]:
        self.logger.info(self.MESSAGES["TERMINATING_CONNECTION"].format(db_name=self.db_name))
        db_name = self.db_name

        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                if not force_disconnect:
                    self.logger.warning(self.MESSAGES["ALREADY_DISCONNECTED"])
                    return message, 409

            self.cursor.close()
            self.db.close()
            self.cursor = None
            self.db = None
            self.db_path = None
            self.db_name = None
            self.connected = False

            message = self.MESSAGES["DISCONNECT_SUCCESS"].format(db_name=db_name)
            self.logger.info(message)
            return message, 200

        except Exception as e:
            message = f"{self.MESSAGES['DISCONNECT_FAIL'].format(db_name=db_name)}: {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Check if table exists
    Parameters:
        table_name (str) - The name of the table to check
    Returns:
        True if table exists, False otherwise
    """
    def _table_exists(self, table_name: str) -> bool:
        try:
            table_name = table_name.strip().lower()
            if not self.valid_name_pattern.match(table_name):
                self.logger.warning(self.MESSAGES["INVALID_TABLE_NAME"].format(table_name=table_name))
                return False

            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return False

            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
            self.cursor.execute(query, (table_name,))
            self.logger.info(f"Checking if table {table_name} exists in database {self.db_name}...")
            exists = self.cursor.fetchone() is not None
            if exists:
                self.logger.info(self.MESSAGES["TABLE_FOUND"].format(table_name=table_name))
                return True
            else:
                self.logger.warning(self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name))
                return False

        except Exception as e:
            self.logger.error(f"Failed to check if table {table_name} exists: {str(e)}")
            return False

    """
    Create table in SQLite Database
    Parameters:
        table_name (str) - The name of the table to create
        force_create (bool) - Whether to force creation if table already exists
    Returns:
        - Message (str)
        - HTTP Status Code (int)
    """
    def create_table(self, table_name: str, columns:List[str], force_create:bool=False) -> Tuple[str, int]:
        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                return message, 400

            if self._table_exists(table_name):
                if not force_create:
                    message = self.MESSAGES["TABLE_EXISTS"].format(table_name=table_name)
                    self.logger.warning(message)
                    return message, 409
                else:
                    self.drop_table(table_name)
                    self.logger.info(f"Table {table_name} deleted.")

            if len(columns) == 0:
                message = "No columns provided for table creation."
                self.logger.error(message)
                return message, 400

            columns = ", ".join(columns)

            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(query)

            self.db.commit()
            message = self.MESSAGES["TABLE_CREATED"].format(table_name=table_name)
            self.logger.info(message)

            return message, 201

        except Exception as e:
            message = f"Failed to create table {table_name}: {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Delete table from SQLite Database
    Parameters:
        table_name (str) - The name of the table to delete
    Returns:
        - Message (str)
        - HTTP Status Code (int)
    """
    def drop_table(self, table_name: str) -> Tuple[str, int]:
        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                return message, 400

            if not self._table_exists(table_name):
                message = self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name)
                self.logger.warning(message)
                return message, 404

            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.cursor.execute(f"VACUUM")
            self.db.commit()

            message = self.MESSAGES["TABLE_DELETED"].format(table_name=table_name)
            self.logger.info(message)

            return message, 200

        except Exception as e:
            message = f"{self.MESSAGES["TABLE_DELETION_FAIL"].format(table_name=table_name)}: {str(e)}"
            self.logger.error(message)
            return message, 500

    def get_primary_key_column(self, table_name: str) -> Optional[str]:
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        primary_key_column = None
        for column_info in self.cursor.fetchall():
            if column_info[5] == 1:  # pk flag is column 5 in PRAGMA table_info
                primary_key_column = column_info[1]  # Index 1 is column name
                break
        return primary_key_column

    """
    Retrieves a row based on primary key from table in SQLite Database
    Parameters:
        - table_name (str) - The name of the table to retrieve row from
        - row_id (str) - The value of the primary key of the row to retrieve
    Returns:
        - A dictionary representing the row of the table if found, None otherwise
        - HTTP Status Code (int)
    """
    def get_row(self, table_name: str, primary_key_value: str) -> Tuple[Optional[dict], int]:
        try:
            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return None, 400

            if not self._table_exists(table_name):
                self.logger.warning(self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name))
                return None, 404

            primary_key_column = self.get_primary_key_column(table_name)

            query = f"SELECT * FROM {table_name} WHERE {primary_key_column} = ?"
            self.cursor.execute(query, (primary_key_value,))
            row = self.cursor.fetchone()

            if row is None:
                self.logger.info(self.MESSAGES["ROW_NOT_FOUND"].format(table_name=table_name, row_id=primary_key_value))
                return None, 404

            column_names = [description[0] for description in self.cursor.description]
            row_data = dict(zip(column_names, row))

            self.logger.info(self.MESSAGES["ROW_RETRIEVAL_SUCCESS"].format(table_name=table_name, row_id=primary_key_value))
            return row_data, 200

        except Exception as e:
            message = f"{self.MESSAGES['ROWS_RETRIEVAL_FAILED'].format(table_name=table_name)}: {str(e)}"
            self.logger.error(message)
            return None, 500

    """
    Retrieves rows from table in SQLite Database based on conditions
    Parameters:
        - table_name (str) - The name of the table to retrieve rows from
        - conditions (List[str]) - A list of conditions to filter the rows by
    Returns:
        - A list of dictionaries representing the rows of the table if found, None otherwise
        - HTTP Status Code (int)
    """
    def get_rows(self, table_name: str, conditions: List[str]) -> Tuple[Optional[List[dict]], int]:
        try:
            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return None, 400

            if not self._table_exists(table_name):
                self.logger.warning(self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name))
                return None, 404

            condition_str = " AND ".join(conditions) if conditions else "1=1"  # Select all if no conditions
            query = f"SELECT * FROM {table_name} WHERE {condition_str}"
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]
            rows = [dict(zip(columns, row)) for row in self.cursor.fetchall()]

            message = self.MESSAGES["ROWS_FOUND"].format(table_name=table_name)
            self.logger.info(message)

            return rows, 200

        except Exception as e:
            message = f"{self.MESSAGES['ROWS_RETRIEVAL_FAILED'].format(table_name=table_name)}: {str(e)}"
            self.logger.error(message)
            return None, 500

    """
    Insert row into table in SQLite Database
    Parameters:
        table_name (str) - The name of the table to insert row into
        row (List[str]) - The row data to insert
    Returns:
        Response message (str)
        HTTP Status Code (int)
    """
    def insert_row(self, table_name: str, row: List[str]) -> Tuple[str, int]:
        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                return message, 400

            if not self._table_exists(table_name):
                message = self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name)
                self.logger.warning(message)
                return message, 404

            placeholders = ", ".join(["?" for _ in row])
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            self.cursor.execute(insert_query, row)
            self.db.commit()

            message = self.MESSAGES["ROW_INSERTED"].format(table_name=table_name)
            self.logger.info(message)
            return message, 201

        except Exception as e:
            message = self.MESSAGES["ROWS_INSERTION_FAIL"].format(table_name=table_name) + f" {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Insert multiple rows into table in SQLite Database
    Parameters:
        - table_name (str) - The name of the table to insert rows into
        - rows (List[List[str]]) - A list of row data to insert
    Returns:
        Response message (str)
        HTTP Status Code (int)
    """
    def insert_rows(self, table_name: str, rows: List[List[str]]) -> Tuple[str, int]:
        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                return message, 400

            if not self._table_exists(table_name):
                message = self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name)
                self.logger.warning(message)
                return message, 404

            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()
            column_names = [info[1] for info in columns_info]

            placeholders = ', '.join(['?' for _ in column_names])
            insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"

            self.cursor.executemany(insert_query, rows)
            self.db.commit()

            message = self.MESSAGES["ROWS_INSERTION_SUCCESS"].format(table_name=table_name)
            self.logger.info(message)

            return message, 201

        except Exception as e:
            message = self.MESSAGES["ROWS_INSERTION_FAIL"].format(table_name=table_name) + f" {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Delete rows from table in SQLite Database
    Parameters:
        - table_name (str) - The name of the table to delete rows from
    Returns:
        - True if rows deleted, False otherwise
        - HTTP Status Code (int)
    """
    def delete_rows(self, table_name: str, conditions: List[str]) -> Tuple[str, int]:
        if not self.connected:
            message = self.MESSAGES["NOT_CONNECTED"]
            self.logger.info(message)
            return message, 400

        if not self._table_exists(table_name):
            message = self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name)
            self.logger.warning(message)
            return message, 404

        try:
            condition_str = " AND ".join(conditions)
            delete_query = f"DELETE FROM {table_name} WHERE {condition_str}"
            self.cursor.execute(delete_query)

            self.db.commit()

            message = self.MESSAGES["ROWS_DELETED"].format(table_name=table_name)
            self.logger.info(message)
            return message, 200

        except Exception as e:
            message = f"{self.MESSAGES['ROWS_DELETION_FAILED'].format(table_name=table_name)} {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Update multiple rows in a table in SQLite Database
    Parameters:
        - table_name (str) - The name of the table to update rows in
        - rows (List[List[str]]) - A list of tuples, each containing the unique identifier followed by the column data
    Returns:
        Response message (str)
        HTTP Status Code (int)
    """

    def update_rows(self, table_name: str, rows: List[List[str]]) -> Tuple[str, int]:
        try:
            if not self.connected:
                message = self.MESSAGES["NOT_CONNECTED"]
                self.logger.info(message)
                return message, 400

            if not self._table_exists(table_name):
                message = self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name)
                self.logger.warning(message)
                return message, 404

            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()
            column_names = [info[1] for info in columns_info]

            if len(column_names) < 2:
                message = "Table must have at least a unique identifier and one field to update."
                self.logger.warning(message)
                return message, 400

            identifier_col = column_names[0]
            update_columns = column_names[1:]

            set_clause = ', '.join([f"{column} = ?" for column in update_columns])
            update_query_template = f"UPDATE {table_name} SET {set_clause} WHERE {identifier_col} = ?"

            with self.db:
                for row in rows:
                    if len(row) != len(column_names):
                        message = f"Row length {len(row)} does not match table column count {len(column_names)}"
                        self.logger.error(message)
                        continue

                    unique_id = row[0]
                    values = row[1:]

                    self.cursor.execute(update_query_template, values + [unique_id])

            self.db.commit()
            message = self.MESSAGES["ROWS_UPDATE_SUCCESS"].format(table_name=table_name)
            self.logger.info(message)

            return message, 200

        except Exception as e:
            message = self.MESSAGES["ROWS_UPDATE_FAIL"].format(table_name=table_name) + f" {str(e)}"
            self.logger.error(message)
            return message, 500

    """
    Retrieve table from SQLite Database
    Parameters:
    table_name - The name of the table to retrieve
    Returns:
        - A list of dictionaries representing the rows of the table if found,
          None otherwise
        - HTTP Status Code (int)
    """
    def get_table(self, table_name: str) -> Tuple[Optional[List[dict]], int]:
        try:
            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return None, 400

            if not self._table_exists(table_name):
                self.logger.warning(self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name))
                return None, 404

            self.logger.info(self.MESSAGES["TABLE_FOUND"].format(table_name=table_name))

            query = f"SELECT * FROM ?"
            self.cursor.execute(query, (table_name,))
            rows = self.cursor.fetchall()

            if not rows:
                self.logger.info(self.MESSAGES["NO_ROWS_FOUND"].format(table_name=table_name))
                return [], 200

            self.logger.info(self.MESSAGES["ROWS_FOUND"].format(table_name=table_name))

            columns = [column[0] for column in self.cursor.description]

            result = [dict(zip(columns, row)) for row in rows]

            self.logger.info(self.MESSAGES["TABLE_RETRIEVED"].format(table_name=table_name))
            return result, 200

        except sqlite3.Error as e:
            self.logger.error(f"Database error occurred while retrieving table {table_name}: {str(e)}")
            return None, 500

        except Exception as e:
            self.logger.error(f"Unexpected error occurred while retrieving table {table_name}: {str(e)}")
            return None, 500

    """
    Retrieves all table data from SQLite Database
    Returns:
        - A dictionary with the names of the tables as keys. Each value is another dictionary containing:
            - "columns": list of str, the names of the columns.
            - "rows": list of tuples, where each tuple represents a row of data from the table.
            Otherwise None If the database is not connected, or if there are no tables, or if an error occurs during retrieval.
        - HTTP Status Code (int)
    """

    def get_tables(self) -> Tuple[Optional[Dict[str, Dict[str, Any]]], int]:
        try:
            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return None, 400

            query = "SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';"
            self.cursor.execute(query)
            table_names = self.cursor.fetchall()

            if not table_names:
                self.logger.info(self.MESSAGES["NO_TABLES_FOUND"])
                return {"tables": {}}, 200

            all_table_data = {}

            for table_name in table_names:
                table_name = table_name[0]
                # Ensure the table_name is safe to use directly in a query
                query = f"SELECT * FROM {table_name}"

                # Execute query without additional bindings since no parameters are required
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                column_names = [description[0] for description in self.cursor.description]
                table_data = {
                    "columns": column_names,
                    "rows": rows
                }
                self.logger.info(f"Table {table_name} data retrieved.")
                all_table_data[table_name] = table_data

            self.logger.info("All table data retrieved.")
            return {"tables": all_table_data}, 200

        except Exception as e:
            self.logger.error(f"Unexpected error occurred while retrieving all table data: {str(e)}")
            return None, 500

    """
    Retrieves the schema of a specified table within the connected SQLite database.
    Parameters:
        - table_name (str) - The name of the table whose schema is to be retrieved
    Returns:
        - Optional[List[dict]] - A list of dictionaries representing the schema of the table.
                                 Each dictionary contains details about a column
        - HTTP Status Code (int)
    """
    def get_table_schema(self, table_name: str) -> Tuple[Optional[List[dict]], int]:
        try:
            if not self.connected:
                self.logger.info(self.MESSAGES["NOT_CONNECTED"])
                return None, 400

            if not self._table_exists(table_name):
                self.logger.warning(self.MESSAGES["TABLE_NOT_FOUND"].format(table_name=table_name))
                return None, 404

            self.cursor.execute(f"PRAGMA table_info({table_name})")
            schema = self.cursor.fetchall()
            if not schema:
                self.logger.warning(f"Table {table_name} schema not found.")
                return None, 404

            self.logger.info(self.MESSAGES["TABLE_SCHEMA_RETRIEVED"].format(table_name=table_name))
            return schema, 200

        except Exception as e:
            self.logger.error(f"Unexpected error occurred while retrieving table schema: {str(e)}")
            return None, 500