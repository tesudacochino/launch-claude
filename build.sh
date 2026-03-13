#!/bin/bash
# Script de compilación a binary con Nuitka
# Uso: ./build.sh [linux|windows]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_CMD="${PYTHON_CMD:-python3}"
NITKA_CMD="${NITKA_CMD:-nuitka3}"

# Función para instalar dependencias
install_deps() {
    echo "📦 Instalando dependencias..."
    $PYTHON_CMD -m pip install --upgrade pip
    $PYTHON_CMD -m pip install -e ".[dev]"
}

# Función para compilar con Nuitka
compile_nuitka(output_name="cl") {
    local target=$1
    local platform=$2

    echo "🔨 Compilando con Nuitka..."

    if [ "$platform" = "windows" ]; then
        $NITKA_CMD \
            --onefile \
            --windows-disable-console \
            --output-filename="$target.exe" \
            --output-dir="." \
            --include-package=claude_launch \
            src/claude_launch/main.py
    else
        $NITKA_CMD \
            --onefile \
            --strip \
            --output-filename="$target" \
            --output-dir="." \
            --include-package=claude_launch \
            src/claude_launch/main.py
    fi

    echo "✅ Binary creado: $target$([[ "$platform" = "windows" ]] && echo ".exe")"
}

# Función para crear entorno virtual con uv
create_venv_uv() {
    if ! command -v uv &> /dev/null; then
        echo "⚠️ uv no está instalado. Instaland..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    uv venv .venv
    source .venv/bin/activate  # o .venv\Scripts\activate en Windows
    uv pip install -e ".[dev]"
}

# Función principal
main() {
    local platform="${1:-auto}"

    case "$platform" in
        linux)
            echo "🐧 Compilando para Linux..."
            compile_nuitka cl linux
            chmod +x cl
            ;;
        windows)
            echo "🪟 Compilando para Windows (con WSL o desde Linux con cross-compilation)..."
            compile_nuitka cl windows
            ;;
        auto)
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                compile_nuitka cl linux
                chmod +x cl
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                compile_nuitka cl darwin
            else
                echo "⚠️ Sistema no reconocido. Especifica linux o windows."
                exit 1
            fi
            ;;
        *)
            echo "❌ Plataforma desconocida: $platform"
            echo "Uso: $0 [linux|windows|auto]"
            exit 1
            ;;
    esac
}

# Instalar dependencias si no están instaladas
install_deps

# Ejecutar compilación
main "$@"
