from flask import jsonify
from src.app import app, flask_api

@app.route('/swagger.json')
def swagger_json():
    return jsonify(flask_api.__schema__)