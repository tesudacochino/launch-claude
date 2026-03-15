@echo off
REM Script de instalacion simple para Windows con uv
REM Uso: install.bat
REM Nota: uv debe estar instalado previamente

REM Crear entorno virtual si no existe
if not exist .venv (
    echo Creando entorno virtual...
    uv venv .venv
)

REM Activar y instalar dependencias
echo Instalando dependencias...
call .venv\Scripts\activate.bat
uv pip install -e .

echo Instalacion completada
