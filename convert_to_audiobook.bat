@echo off
setlocal

REM Path to your venv
set VENV_PATH=venv
set SCRIPT_PATH=to_audiobook.py

REM If dragged-in file exists, use it
if exist "%~1" (
    set INPUT_FILE=%~1
) else (
    echo No file dragged. Please enter file path:
    set /p INPUT_FILE="File: "
)

REM Activate venv
call "%VENV_PATH%\Scripts\activate.bat"

REM Run script with the file path
python "%SCRIPT_PATH%" "%INPUT_FILE%"

pause