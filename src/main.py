"""
This class is the starting point and is responsible for initiating the server and streamlit app
"""

import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))

if project_root not in sys.path:
    sys.path.append(project_root)

import subprocess
import threading
import time
import requests
import app_config

os.environ['FLASK_APP'] = 'src/app/main.py'

config = app_config.load()

def run_flask():
    debug = config['debug']
    host = config['host']
    port = config['flask_port']
    use_reloader = config['use_reloader']

    command = [
        "flask", "run",
        "--host", host,
        "--port", str(port)
    ]

    if debug:
        command.append("--debug")

    if use_reloader:
        command.append("--reload")

    process = subprocess.Popen(command)
    process.wait()

def run_streamlit():
    process = subprocess.Popen(["streamlit", "run", "src/dashboard/streamlit_app.py"])
    process.wait()

def await_flask(url, timeout=20):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

def run():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    flask_ready = await_flask(config['flask_url'])

    if flask_ready:
        print(f"Flask is ready at {config['flask_url']}\nStarting Streamlit at {config['streamlit_url']}...")
        run_streamlit()
        return 0
    else:
        print("Flask did not start in time, exiting.")
        return -1

if __name__ == '__main__':
    run()
