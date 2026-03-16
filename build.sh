#!/bin/bash
# Script de compilación a binary con PyInstaller
# Uso: ./build.sh

set -e

echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Compilando con PyInstaller..."
mkdir -p dist
pyinstaller --onefile --console --name ccl src/claude_launch/main.py

chmod +x dist/ccl
echo "Binary creado: dist/ccl"
