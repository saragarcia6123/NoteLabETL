import subprocess
import threading
import time
import json
import requests
from app import app
import sys

with open('config.json') as config_file:
    config = json.load(config_file)

HOST = config['HOST']
FLASK_PORT = int(config['FLASK_PORT'])
STREAMLIT_PORT = int(config['STREAMLIT_PORT'])
DEBUG = config['DEBUG'] == 'True'

FLASK_URL = f"http://{HOST}:{FLASK_PORT}"
STREAMLIT_URL = f"http://{HOST}:{STREAMLIT_PORT}"

def run_flask():
    app.run(debug=True, port=5000, use_reloader=False)

def run_streamlit():
    subprocess.run(["streamlit", "run", "dashboard/Home.py"])

def await_flask(url, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

def main():
    try:
        subprocess.run([sys.executable, 'setup.py', 'install'], check=True)
        print("setup.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running setup.py: {e}")
        return

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    flask_ready = await_flask(FLASK_URL)

    if flask_ready:
        print(f"Flask is ready at {FLASK_URL}\nStarting Streamlit at {STREAMLIT_URL}...")
        run_streamlit()
        return 0
    else:
        print("Flask did not start in time, exiting.")
        return -1

if __name__ == '__main__':
    main()
