import argparse
import os
import logging
from flask import Flask
from flask_restx import Api
from app.routes import sqlite
from app.routes.sqlite import sqlite_api

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

sqlite.init_routes(flask_api)
sqlite.set_logger(app.logger)

def run(debug, host, port, use_reloader, logger):
    try:
        app.logger.info(f"Starting Flask server on {host}:{port} with debug={debug}, use_reloader={use_reloader}...")
        app.run(debug=debug, host=host, port=port, use_reloader=use_reloader, logger=logger)
    finally:
        print("Shutting down Flask server...")
        sqlite_api.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask server with specified parameters.')

    parser.add_argument('--debug', type=bool, default=False, help='Enable or disable debug mode.')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host on which to run the server.')
    parser.add_argument('--port', type=int, default=5000, help='Port on which to run the server.')
    parser.add_argument('--use_reloader', type=bool, default=False, help='Enable or disable reloader.')

    args = parser.parse_args()

    run(debug=args.debug, host=args.host, port=args.port, use_reloader=args.use_reloader, logger=logger)