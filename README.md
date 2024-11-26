
## NoteLab - 0.1.0

## Description
NoteLab, WIP Streamlit+Flask project

## The following is the directory structure of the project:
src/
    init.py
    config.json
    database/
        database
    utils/
        classifier.py
        querify.py
        sqlite_loader.py
        api/
            genius_api.py
            spotify_api.py
    dashboard/
        Home.py
        config.py
        .streamlit/
            config.toml
        pages/
            API.py
            Tables.py
        __pycache__/
            config.cpython-312.pyc
    server/
        server.py
        __pycache__/
            server.cpython-312.pyc
        templates/
            index.html
    __pycache__/
        init.cpython-312.pyc


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/NoteLabETL.git
    cd NoteLabETL
    ```

2. Set up environment (optional, recommended):

    Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

    OR

    Set up a Conda environment (recommended):
    ```bash
    conda create -n notelabenv python=3.12
    conda activate notelabenv
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the app, use the following command:
    ```bash
    python -m src.init
    ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
