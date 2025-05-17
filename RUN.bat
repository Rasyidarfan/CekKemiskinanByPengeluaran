@echo off
echo FASIH BPS Backup Modifier
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python tidak ditemukan. Silakan install Python terlebih dahulu.
    echo Anda dapat mengunduh Python dari https://www.python.org/downloads/
    pause
    exit /b
)

REM Create virtual environment if it doesn't exist
if not exist \"venv\\\" (
    echo Membuat virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Mengaktifkan virtual environment...
call venv\\Scripts\\activate.bat

REM Check if required packages are installed
echo Memeriksa dan menginstall modul yang diperlukan...
python -m pip install --upgrade pip
python -m pip install streamlit pycryptodome

REM Run the application
echo.
echo Menjalankan aplikasi FASIH BPS Backup Modifier...
cls
streamlit run app.py

REM Deactivate virtual environment before exiting
call venv\\Scripts\\deactivate.bat

pause