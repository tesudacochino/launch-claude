#!/bin/bash
# Script de instalación simple
# Uso: ./install.sh

set -e

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -e ".[dev]"

echo "Instalación completada"
