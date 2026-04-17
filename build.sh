#!/usr/bin/env bash
# Build binary with PyInstaller (Linux/macOS)
# Usage: ./build.sh

set -e

echo "===================================================="
echo " Building claude-launch with PyInstaller"
echo "===================================================="
echo

# Detect python from venv or system
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

# Install dependencies + pyinstaller
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip >/dev/null 2>&1 || true
$PYTHON_CMD -m pip install -e ".[build]"

echo
echo "Building binary..."
echo

# Build with PyInstaller using the spec file
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
