# Claude Launch 🚀

Lanzador de **Claude Code** con soporte para múltiples providers Ollama.

Similar a `ccl mole` y `ccl chati` que tienes en OpenCode, pero adaptado para Claude Code.

## 📋 Requisitos

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes rápido)
- Ollama corriendo en los endpoints configurados

## 🚀 Instalación Rápida

```bash
# Clonar el proyecto
git clone <repo-url>
cd claude-launch

# Instalar todo (dependencias + configuración inicial)
./install.sh all

# Usar el CLI
./scripts/ccl mole          # Selecciona un modelo e interactúa con Claude
./scripts/ccl chati         # Otro provider distinto
./scripts/ccl mole --model mistral:latest  # Directo a un modelo específico
./scripts/ccl --new         # Agregar nuevo provider
```

## 🛠️ Estructura del Proyecto

```
claude-launch/
├── pyproject.toml          # Metadatos + dependencias
├── config.json             # Configuración de providers (tuya)
├── install.sh              # Script de instalación con uv
├── build.sh                # Compilación a binary con pyinstaller
├── README.md               # Este archivo
├── src/
│   └── claude_launch/
│       ├── __init__.py     # Exportaciones públicas
│       ├── config.py       # Manejo de configuración
│       ├── ollama_api.py   # Comunicación con Ollama API
│       ├── launcher.py     # Ejecución de Claude Code
│       ├── cli.py          # Interfaz interactiva con Rich
│       └── main.py         # Entry point CLI
├── scripts/
│   ├── ccl                  # Wrapper para Linux/macOS
│   └── ccl.bat              # Wrapper para Windows
```

## 🔧 Configuración

El archivo `config.json` sigue el formato de OpenCode:

```json
{
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
    "options": {
      "base_url": "http://your-ollama-server:11434",
      "api_key": "ollama"
    },
    "models": { ... }
  }
}
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `./scripts/ccl` | Muestra la ayuda y providers disponibles |
| `./scripts/ccl <provider>` | Lista modelos e interactúa con Claude |
| `./scripts/ccl <provider> --model <name>` | Lanza directo a un modelo específico |
| `./scripts/ccl --new` | Asistente para agregar nuevo provider |

### Ejemplos de Uso

```bash
# Interactivo - selecciona un modelo
./scripts/ccl mole

# Directo a modelo específico
./scripts/ccl chati --model qwen3.5:122b

# Agregar nuevo provider
./scripts/ccl --new

# Con config personalizado
./scripts/ccl --config /ruta/a/config.json mole
```

## 📦 Compilación a Binary

### Usando PyInstaller

```bash
# Instalar pyinstaller
pip install pyinstaller

# Compilar para tu sistema actual
./build.sh

# Output generado:
# - dist/ccl    - Binary ejecutable para Linux/macOS
# - dist/ccl.exe - Binary ejecutable para Windows
```

## 🧪 Desarrollo

```bash
# Crear entorno virtual con uv
uv venv .venv
source .venv/bin/activate

# Instalar en modo desarrollo
uv pip install -e ".[dev]"

# Ejecutar directamente (sin wrapper)
python -m claude_launch.main mole --model mistral:latest
```

## 🔄 Instrucciones para otra sesión

Para recrear este proyecto desde cero en otra sesión:

1. **Crea el proyecto:**
   ```bash
   mkdir claude-launch && cd claude-launch
   git init
   ```

2. **Copia los archivos esenciales:**
   - `pyproject.toml` - Configuración del proyecto y dependencias
   - `config.json` - Tu configuración de providers (la que ya tienes)
   - `src/claude_launch/` - Todos los módulos Python
   - `scripts/ccl` y `scripts/ccl.bat` - Wrappers para ejecutar el CLI
   - `install.sh` - Script de instalación con uv
   - `build.sh` - Script de compilación con pyinstaller

3. **Ejecuta la instalación:**
   ```bash
   ./install.sh all
   ```

4. **Verifica que funciona:**
   ```bash
   # Deberías ver el menú o información del CLI
   ./scripts/ccl --help
   ./scripts/ccl mole  # (si tienes el provider mole configurado)
   ```

5. **(Opcional) Compila a binary:**
   ```bash
   ./build.sh auto
   # Esto generará el ejecutable 'ccl'
   ```

## 📝 Notas importantes

1. **Antropik Code API**: El script configura las variables de entorno `ANTHROPIC_BASE_URL` y `ANTHROPIC_API_KEY` para cada provider, permitiendo conectar a endpoints Ollama compatibles con la API de Anthropic.

2. **Seguridad**: Las credenciales de los endpoints se manejan localmente. No se envían datos externos sin tu control explícito.

3. **Cross-platform**: Funciona en Linux, macOS y Windows (WSL o nativo).

## License

MIT License - ver `LICENSE` file included.
