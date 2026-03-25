#!/usr/bin/env bash
# Script de compilación a binary con PyInstaller (Linux/macOS)
# Uso: ./build.sh

set -e

echo "===================================================="
echo " Building claude-launch with PyInstaller"
echo "===================================================="
echo

# Detectar python del venv o sistema (Linux y macOS)
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "Using virtual environment Python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Using system Python (python3)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "Using system Python (python)"
else
    echo "Error: Python not found"
    exit 1
fi

# Asegurar pip
if ! $PYTHON_CMD -m ensurepip --upgrade >/dev/null 2>&1; then
    echo "Warning: ensurepip failed, trying pip directly..."
fi

# Instalar dependencias
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip >/dev/null 2>&1 || true
$PYTHON_CMD -m pip install -r requirements.txt

echo
echo "Building binary..."
echo

# Compilar con PyInstaller usando el spec file
$PYTHON_CMD -m PyInstaller --clean ccl.spec --noconfirm

echo
echo "===================================================="
echo " BUILD SUCCESSFUL"
echo "===================================================="
echo " Output: dist/ccl"
echo "===================================================="
echo

if [ -f "dist/ccl" ]; then
    chmod +x dist/ccl
    echo "Binary size:"
    ls -lh dist/ccl
    echo
    echo "To test the binary, run: ./dist/ccl --help"
fi
