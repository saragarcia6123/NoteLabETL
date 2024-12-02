#!/bin/bash

python3 -m venv venv
source venv/bin/activate

pip install poetry
poetry install

export PYTHONPATH="$PWD/src:$PYTHONPATH"

echo "Environment is set up. Run the application using 'python src/main.py'."