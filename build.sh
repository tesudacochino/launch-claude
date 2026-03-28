#!/bin/bash
# Script de compilación a binary con PyInstaller
# Uso: ./build.sh

set -e

echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Compilando con PyInstaller..."
mkdir -p dist
pyinstaller --onefile --console --name ccl \
  --hidden-import=claude_launch.config \
  --hidden-import=claude_launch.cli \
  --hidden-import=claude_launch.ollama_api \
  --hidden-import=claude_launch.launcher \
  --hidden-import=rich \
  --hidden-import=pydantic \
  --hidden-import=openai \
  src/claude_launch/main.py

chmod +x dist/ccl
echo "Binary creado: dist/ccl"
