#!/bin/bash
# Script de compilación a binary con PyInstaller
# Uso: ./build.sh

set -e

echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Compilando con PyInstaller..."
mkdir -p dist
pyinstaller --onefile --console --name cl src/claude_launch/main.py

chmod +x dist/cl
echo "Binary creado: dist/cl"
