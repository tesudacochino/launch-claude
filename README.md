# Claude Launch 🚀

Lanzador de **Claude Code** que se conecta a diferentes endpoints Ollama. Usa `ccl` para seleccionar modelos e interactuar con Claude Code desde cualquier proveedor Ollama compatible.

## ⚡ Instalación Rápida

```bash
# Clonar el proyecto
git clone <repo-url>
cd claude-launch

# Instalar con pip
pip install -e .

# O con uv
uv pip install -e .

# Empezar a usar
ccl
```

## 🚀 Cómo Usar

### Ver todos los providers configurados

```bash
ccl --list
```

### Seleccionar un modelo (modo interactivo)

```bash
ccl mole
# Muestra una lista numerada de modelos disponibles
# Ingresa el número para seleccionar
```

### Lanzar directamente con un modelo específico

```bash
ccl mole --model mistral:latest
ccl chati --model qwen3.5:35b
```

### Agregar un nuevo provider

```bash
ccl --new
# Asistente interactivo para configurar un nuevo endpoint Ollama
```

### Usar con un archivo de configuración personalizado

```bash
ccl --config /ruta/a/config.json <provider>
```

### Pasar flags a Claude Code

```bash
# Después de -- todo se pasa a Claude Code
ccl mole --model mistral:latest -- --dangerously-skip-permissions
ccl mole --model qwen3.5:35b -- --verbose --timeout=60
```

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `ccl` | Mostrar ayuda y menú principal |
| `ccl <provider>` | Lista modelos e interactuar con Claude |
| `ccl <provider> --model <name>` | Lanzar modelo específico directamente |
| `ccl --new` | Asistente para agregar nuevo provider |
| `ccl --list` o `-l` | Listar providers configurados |
| `ccl -r <provider>` | Eliminar un provider |
| `ccl --config <path>` | Usar archivo de configuración personalizado |

## 📦 Compilar Binary

Los binarios se generan automáticamente con GitHub Actions al crear un tag `v*`. Para build local:

```bash
pip install -e '.[build]'
python -m PyInstaller --clean ccl.spec --noconfirm
# Salida: dist/ccl (Linux/macOS) o dist/ccl.exe (Windows)
```

## 📁 Configuración

El archivo `config.json` define los providers:

```json
{
  "mole": {
    "type": "ollama",
    "options": {
      "base_url": "http://127.0.0.1:11434",
      "api_key": "ollama"
    },
    "models": {}
  }
}
```

**Nota:** `models` es opcional - se cargan automáticamente desde el endpoint.

## 🔗 Documentación

- [CLAUDE.md](./CLAUDE.md) - Guía para desarrollar en este repositorio con Claude Code

## Licencia

MIT License - ver archivo `LICENSE`.
