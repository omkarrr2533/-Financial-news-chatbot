@echo off
echo ============================================================
echo   FINANCIAL NEWS IMPACT ANALYZER - QUICK START
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if requirements are installed
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file from .env.example and add your API key
    echo.
    pause
    exit /b 1
)

REM Start the application
echo.
echo Starting application...
echo.
python run.py

pause