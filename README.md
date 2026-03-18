# Claude Launch 🚀

Lanzador de **Claude Code** que se conecta a diferentes endpoints Ollama. Usa `ccl` para seleccionar modelos e interactuar con Claude Code desde cualquier proveedor Ollama compatible.

## ⚡ Instalación Rápida

```bash
# Clonar el proyecto
git clone <repo-url>
cd claude-launch

# Instalar dependencias
./install.sh           # Linux/macOS
# o
install.bat            # Windows

# Empezar a usar
./scripts/ccl
```

## 🚀 Cómo Usar

### Ver todos los providers configurados

```bash
./scripts/ccl --list
```

### Seleccionar un modelo (modo interactivo)

```bash
./scripts/ccl mole
# Muestra una lista numerada de modelos disponibles
# Ingresa el número para seleccionar
```

### Lanzar directamente con un modelo específico

```bash
./scripts/ccl mole --model mistral:latest
./scripts/ccl chati --model qwen3.5:35b
```

### Agregar un nuevo provider

```bash
./scripts/ccl --new
# Asistente interactivo para configurar un nuevo endpoint Ollama
```

### Usar con un archivo de configuración personalizado

```bash
./scripts/ccl --config /ruta/a/config.json <provider>
```

### Pasar flags a Claude Code

```bash
# Despu\u00e9s de -- todo se pasa a Claude Code
./scripts/ccl mole --model mistral:latest -- --dangerously-skip-permissions
./scripts/ccl mole --model qwen3.5:35b -- --verbose --timeout=60
```

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `./scripts/ccl` | Mostrar ayuda y menú principal |
| `./scripts/ccl <provider>` | Lista modelos e interactuar con Claude |
| `./scripts/ccl <provider> --model <name>` | Lanzar modelo específico directamente |
| `./scripts/ccl --new` | Asistente para agregar nuevo provider |
| `./scripts/ccl --list` o `-l` | Listar providers configurados |
| `./scripts/ccl -r <provider>` | Eliminar un provider |
| `./scripts/ccl --config <path>` | Usar archivo de configuración personalizado |

## 📦 Compilar Binary

Crear un ejecutable auto-contenido:

**Linux/macOS:**
```bash
./build.sh
# Salida: dist/ccl
```

**Windows:**
```powershell
build.bat
# Salida: dist/ccl.exe
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

- [Documentación Técnica](./DOCUMENTACION_TECNICA.md) - Arquitectura, desarrollo, detalles de configuración
- [CLAUDE.md](./CLAUDE.md) - Guía para desarrollar en este repositorio con Claude Code

## Licencia

MIT License - ver archivo `LICENSE`.
