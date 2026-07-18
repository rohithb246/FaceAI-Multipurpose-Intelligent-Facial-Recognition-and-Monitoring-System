@echo off
setlocal
set "PYTHONUTF8=1"
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%.runtime\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Missing .runtime environment.
    echo Create one with: python -m venv .runtime
    echo Then install dependencies with: .runtime\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%PROJECT_DIR%app.py"
endlocal
