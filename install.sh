#!/bin/bash
# Script de instalación simple
# Uso: ./install.sh
# Instala dependencias usando pip desde pyproject.toml

set -e

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -e ".[dev]"

echo "Instalación completada"
