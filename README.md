
## NoteLab - 0.1.2
## Authors: saragarcia6123 <saragarcia6123@gmail.com>
## License: MIT

## Description
Work-in-progress SQLite + Flask + Streamlit Dashboard for Data analysis and API interaction

## The following is the directory structure of the project:
```
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
        config.py
        request_handler.py
        streamlit_app.py
        message_handler.py
        Pages/
            Table/
                Tables.py
                create.py
                edit.py
            Main/
                API Documentation.py
                Dashboard.py
    server/
        server.py
        api/
            sqlite_api.py

```

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

    Set up a Conda environment:
    ```bash
    conda create -n notelabenv
    conda activate notelabenv
    ```

3. Install dependencies:
    ```bash
    pip install poetry
    poetry install
    ```

## Usage

To run the app, use the following command:
    ```bash
    python -m src.init
    ```
