
## NoteLab - 0.1.3
## Authors: saragarcia6123 <saragarcia6123@gmail.com>
## License: MIT

## Description
Work-in-progress SQLite + Flask + Streamlit Dashboard for Data analysis and API interaction

## The following is the directory structure of the project:
```
src/
    app_config.py
    app_config.json
    main.py
    __init__.py
    utils/
        pandas_to_sql.py
        song_querifier.py
    app/
        main.py
        __init__.py
        api/
            genius_api.py
            spotify_api.py
            sqlite_api.py
        routes/
            sqlite.py
            swagger.py
        utils/
            async_request_handler.py
            request_handler.py
            http_errors.py
    dashboard/
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
    database/
        database

```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/saragarcia6123/NoteLab.git
    cd NoteLab
    ```

2. **Run the setup script:**
   ```sh
   ./setup_env.sh
   ```

3. **Run the application:**
   ```sh
   python src/main.py
   ```
