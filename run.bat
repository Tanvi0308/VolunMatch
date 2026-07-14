@echo off
echo ===================================================
echo   VolunMatch - AI Volunteer Recommendation System
echo ===================================================
echo.

if not exist "venv" (
    echo [1/3] Creating Python Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Is Python installed correctly?
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment already exists.
)

echo.
echo [2/3] Activating environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Starting the application! (Press Ctrl+C to stop)
echo The database will be initialized automatically.
echo Open your browser to http://127.0.0.1:5000
echo.
python app.py

pause
