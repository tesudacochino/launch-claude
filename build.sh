#!/bin/bash
# Script de compilación a binary con Nuitka
# Uso: ./build.sh

set -e

echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Compilando con Nuitka..."
nuitka3 --onefile --strip --output-filename=cl --output-dir=. --include-package=claude_launch src/claude_launch/main.py

chmod +x cl
echo "Binary creado: cl"
