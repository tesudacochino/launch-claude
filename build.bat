@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo  Building claude-launch for Windows with PyInstaller
echo ====================================================
echo.

REM Usar python del entorno virtual si existe, sino el del sistema
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON_CMD=python
    echo Using system Python
)

REM Asegurar pip
%PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1
if errorlevel 1 (
    echo Error: Python pip not found
    pause
    exit /b 1
)

REM Instalar dependencias
echo Installing dependencies...
%PYTHON_CMD% -m pip install --upgrade pip >nul 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building Windows binary...
echo.

REM Compilar con PyInstaller
%PYTHON_CMD% -m PyInstaller --clean ^
    --onefile ^
    --name=cl ^
    --hidden-import=claude_launch.config ^
    --hidden-import=claude_launch.cli ^
    --hidden-import=claude_launch.ollama_api ^
    --hidden-import=claude_launch.launcher ^
    --hidden-import=rich ^
    --hidden-import=pydantic ^
    --console ^
    --noconfirm ^
    src/claude_launch/main.py

if errorlevel 1 (
    echo.
    echo ====================================================
    echo  BUILD FAILED
    echo ====================================================
    pause
    exit /b 1
)

echo.
echo ====================================================
echo  BUILD SUCCESSFUL
echo ====================================================
echo  Output: dist/cl.exe
echo ====================================================
echo.

if exist dist\cl.exe (
    echo Binary size:
    dir dist\cl.exe | find "cl.exe"
    echo.
    echo To test the binary, run: dist\cl.exe --help
)

rem pause
