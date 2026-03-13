#!/bin/bash
# Script de instalación con uv
# Uso: ./install.sh [setup|run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Función para instalar uv si no existe
ensure_uv() {
    if ! command -v uv &> /dev/null; then
        echo "📦 Instalando uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc  # o ~/.zshrc según corresponda
    fi

    echo "✅ uv está instalado"
}

# Instalar dependencias del proyecto
install_deps() {
    echo "📦 Instalando dependencias con uv..."

    # Crear venv si no existe
    if [ ! -d ".venv" ]; then
        uv venv .venv
    fi

    # Activar y instalar
    source .venv/bin/activate  # o .venv\Scripts\activate en Windows
    uv pip install -e ".[dev]"

    echo "✅ Dependencias instaladas exitosamente"
}

# Ejecutar el CLI
run() {
    if [ ! -d ".venv" ]; then
        echo "⚠️ Entorno virtual no encontrado. Ejecutando './install.sh' primero..."
        ./install.sh install
    fi

    source .venv/bin/activate
    python -m claude_launch.main "$@"
}

# Configuración inicial (crear config.json si no existe)
setup() {
    if [ ! -f "config.json" ]; then
        echo "📝 Creando configuración inicial..."
        cp config.json.example config.json 2>/dev/null || true

        # Si no hay example, crear uno básico
        if [ ! -f "config.json" ]; then
            cat > config.json << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "share": "disabled",
  "tools": {
    "write": true,
    "edit": true,
    "bash": true
  },
  "mole": {
    "type": "ollama",
    "name": "mole",
    "options": {
      "base_url": "http://127.0.0.1:11434",
      "api_key": "ollama"
    },
    "models": {
      "mistral:latest": {"name": "mistral:latest"},
      "qwen3:32b": {"name": "qwen3:32b"}
    }
  },
  "chati": {
    "type": "ollama",
    "name": "chati",
    "options": {
      "base_url": "http://your-ollama-server:11434",
      "api_key": "ollama"
    },
    "models": {
      "mistral:latest": {"name": "mistral:latest"},
      "qwen3.5:122b": {"name": "qwen3.5:122b"}
    }
  }
}
EOF
            echo "✅ config.json creado con configuración de ejemplo"
        fi
    else
        echo "✅ config.json ya existe"
    fi
}

# Función principal
case "${1:-install}" in
    install|deps)
        ensure_uv
        install_deps
        ;;
    setup)
        setup
        ensure_uv
        install_deps
        ;;
    run|exec)
        shift
        run "$@"
        ;;
    all)
        ensure_uv
        setup
        install_deps
        echo "✅ Instalación completa completada"
        ;;
    *)
        echo "Uso: $0 [install|setup|run|all]"
        echo ""
        echo "Comandos:"
        echo "  install   - Instalar dependencias con uv"
        echo "  setup     - Configurar config.json si no existe"
        echo "  run       - Ejecutar el CLI 'cl'"
        echo "  all       - Ejecutar todos los pasos anteriores"
        ;;
esac
