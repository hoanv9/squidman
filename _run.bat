@echo off
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)

:: Check if virtual environment exists
IF NOT EXIST "venv" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate
    
    echo [INFO] Upgrading pip...
    python -m pip install --upgrade pip
    
    IF EXIST "requirements.txt" (
        echo [INFO] Installing dependencies from requirements.txt...
        pip install -r requirements.txt
    ) ELSE (
        echo [WARNING] requirements.txt not found! Skipping dependency installation.
    )
) ELSE (
    echo [INFO] Virtual environment found. Activating...
    call venv\Scripts\activate
)

:: Start the application
echo [INFO] Starting Squid Manager...
python run.py

pause
