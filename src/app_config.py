import json
import os
from gnome_abrt.config import singleton

@singleton
def load():
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, 'app_config.json')

    with open(config_path) as config_file:
        config = json.load(config_file)

    return {
        'host': config['host'],
        'flask_port': config['flask_port'],
        'flask_url': f"http://{config['host']}:{config['flask_port']}",
        'streamlit_port': config['streamlit_port'],
        'streamlit_url': f"http://{config['host']}:{config['streamlit_port']}",
        'debug': config['debug'] == 'True',
        'use_reloader': config['use_reloader'] == 'True',
        'endpoints': config['endpoints'],
    }
