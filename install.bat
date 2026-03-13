@echo off
setlocal enabledelayedexpansion
REM Script de instalacion con uv para Windows
REM Uso: install.bat [install|run|all]

cd /d "%~dp0"

echo ========================================
echo   Claude Launch - Instalador Windows
echo ========================================
echo.

REM Verificar uv
call :check_uv

REM Instalar dependencias del proyecto
call :install_deps

REM Configurar config.json si no existe
call :setup_config

echo.
echo ================================
echo   Instalacion completada!
echo ================================
echo.
echo Puedes ejecutar el CLI con:
echo   scripts\cl mole
echo   scripts\cl chati --model qwen3.5:122b
echo   scripts\cl --new
echo.
exit /b 0

REM --- Funciones ---

:check_uv
    echo [INFO] Verificando uv...
    uv --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo   'uv' no encontrado, instalando...
        REM Usar py -m pip para instalar uv sin depender de venv
        py -m pip install --upgrade uv || python -m pip install --upgrade uv
    ) else (
        echo   Uv ya instalado
    )
    goto end_check_uv

:end_check_uv
    goto :eof

:install_deps
    echo [INFO] Instalando dependencias con uv...

    REM Crear venv si no existe usando uv directamente
    if not exist ".venv" (
        echo   Creando entorno virtual con uv...
        uv venv .venv
    )

    REM Activar y usar uv para instalar
    call .venv\Scripts\activate.bat
    uv pip install -e "."

    echo   Uv Dependencias instaladas
    goto :eof

:setup_config
    if not exist "config.json" (
        echo [INFO] Creando config.json de ejemplo...
        echo { > config.json
        echo ^  "mole": {^} >> config.json
        echo     "type": "ollama", >> config.json
        echo     "name": "mole", >> config.json
        echo     "options": { >> config.json
        echo       "base_url": "http://127.0.0.1:11434", >> config.json
        echo       "api_key": "ollama" >> config.json
        echo     }, >> config.json
        echo     "models": { >> config.json
        echo       "mistral:latest": {"name": "mistral:latest"} >> config.json
        echo     } >> config.json
        echo   } >> config.json

        echo   Uv config.json creado
    ) else (
        echo   Uv config.json ya existe
    )
    goto :eof
