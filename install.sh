#!/usr/bin/env bash
# Script de instalacion para Linux/macOS
# Uso: ./install.sh

set -e

echo "===================================================="
echo " Installing claude-launch"
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
$PYTHON_CMD -m pip install -e ".[dev]"

echo
echo "===================================================="
echo " INSTALLATION COMPLETE"
echo "===================================================="
echo "To run the CLI: source .venv/bin/activate && python -m claude_launch.main --help"
echo "Or use: ./scripts/ccl --help"
echo "===================================================="
echo
