@echo off
REM Batch wrapper para Windows - ejecuta Claude Launch desde cmd/PowerShell
set SCRIPT_DIR=%~dp0

REM Habilitar UTF-8 para soportar emojis y caracteres especiales
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Intenta encontrar Python en el entorno virtual o en el PATH
if exist "%SCRIPT_DIR%..\.venv\Scripts\python.exe" (
    set PYTHON_EXE=%SCRIPT_DIR%..\.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

set PYTHONPATH=%SCRIPT_DIR%..\src;%PYTHONPATH%

%PYTHON_EXE% -m claude_launch.main %*
