@echo off
REM Setup script for Gemini API Wrapper - Windows

echo.
echo ========================================
echo Gemini API Wrapper - Setup Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python found: 
python --version
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.
echo.

REM Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed.
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a .env file and add your Gemini API key:
echo    Copy .env.example to .env
echo    Add your key from: https://aistudio.google.com/app/apikeys
echo.
echo 2. Start the API server:
echo    python main.py
echo.
echo 3. In another terminal, start Streamlit UI:
echo    streamlit run app.py
echo.
echo 4. Test with Postman:
echo    Import Gemini_API_Wrapper.postman_collection.json
echo.
echo 5. Optional security scan:
echo    security_scan.bat
echo.
pause
