# Documentación Técnica - Claude Launch

Documentación técnica para desarrolladores. [Volver al README](./README.md)

## 🏗️ Arquitectura

### Estructura del Proyecto

```
claude-launch/
├── pyproject.toml          # Metadatos, dependencias, configuración hatch
├── config.json             # Configuración de providers (OpenCode-style)
├── requirements.txt        # Dependencias directas
├── LICENSE                 # Licencia MIT
├── README.md               # Documentación para usuarios
├── DOCUMENTACION_TECNICA.md # Esta guía técnica
├── CLAUDE.md              # Guía para desarrolladores Claude Code
├── src/claude_launch/      # Paquete principal de Python
│   ├── __init__.py         # Exportaciones públicas
│   ├── main.py             # Entry point CLI con argparse
│   ├── config.py           # Manejo de configuración
│   ├── cli.py              # Interfaz Rich (UI interactiva)
│   ├── ollama_api.py       # Cliente API para Ollama
│   └── launcher.py         # Launcher de Claude Code
├── scripts/                # Wrappers de CLI
│   ├── ccl                  # Wrapper Linux/macOS
│   └── ccl.bat              # Wrapper Windows
├── install.sh               # Script instalación Linux/macOS
├── install.bat              # Script instalación Windows
├── build.sh                 # Script compilación Linux/macOS
├── build.bat                # Script compilación Windows
└── cl.spec                  # Especificación PyInstaller Windows
```

### Componentes Principales

#### `src/claude_launch/main.py`

Entry point principal con argparse. Maneja:
- Parsed de argumentos CLI
- Dispatch a modos: interactive, direct launch, add provider, list, remove
- Filtrado de args extra después de `--` para pasar a Claude Code

```python
# Ejemplo de uso
python -m claude_launch.main mole --model mistral:latest
python -m claude_launch.main --new
```

#### `src/claude_launch/config.py`

Manejo de configuración con formato **OpenCode-style**:
- `ConfigWrapper`: Parsea config.json, filtra metadata keys (`$schema`, `share`, `tools`)
- `ProviderConfig`: Define provider (type, options, models)
- `ProviderOptions`: Pydantic model para `base_url` y `api_key`
- `ModelConfig`: Configuración de modelo individual

Formato de configuración (OpenCode-style):
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

**Campos:**
- `mole` = nombre único del provider (clave JSON)
- `type` = tipo de endpoint (`"ollama"`)
- `options.base_url` = URL del endpoint Ollama
- `options.api_key` = API key para autenticación
- `models` = dict de modelos disponibles (opcional, se fetchea en runtime)

Características clave:
- Providers en root level (no bajo `providers` key)
- Soporta `base_url`/`baseURL` y `api_key`/`apiKey`
- Models dict es opcional (se fetchea en runtime)

#### `src/claude_launch/cli.py`

Interfaz de usuario con **Rich**:
- `show_main_menu()`: Muestra tabla de providers disponibles
- `show_provider_models()`: Muestra modelos numerados
- `select_model()`: Prompt para selección de modelo
- `run_provider_selection()`: Flujo interactivo completo
- `run_new_provider()`: Asistente para agregar providers

#### `src/claude_launch/ollama_api.py`

Cliente API para endpoints Ollama:
- `list_models()`: Obtiene lista de modelos (soporta formatos OpenAI y nativo Ollama)
- `check_model_exists()`: Verifica existencia de modelo específico
- `test_connection()`: Prueba conectividad al endpoint

Maneja tres formatos de respuesta:
```python
# Formato OpenAI
{"data": [{"id": "model1"}, ...]}

# Formato Ollama nativo
["model1", "model2", ...]

# Otro formato común
{"models": [{"name": "model1"}, ...]}
```

#### `src/claude_launch/launcher.py`

`ClaudeLauncher`: Subprocess launcher para Claude Code
- Inyecta variables de entorno específicas por provider
- Lanza `claude` executable con flags configurados

```python
from claude_launch.launcher import ClaudeLauncher

launcher = ClaudeLauncher(
    base_url="http://127.0.0.1:11434",
    api_key="ollama",
    model="qwen3.5:35b",
    dangerously_skip_permissions=False,
    extra_args=["--verbose"]
)
exit_code = launcher.launch_interactive()
```

## 🔧 Variables de Entorno

El launcher inyecta estas variables al proceso de Claude Code:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ANTHROPIC_BASE_URL` | Endpoint Ollama | `http://127.0.0.1:11434/v1` |
| `ANTHROPIC_AUTH_TOKEN` | API key | `ollama` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Modelo Haiku | `qwen3.5:35b` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Modelo Opus | `qwen3.5:35b` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Modelo Sonnet | `qwen3.5:35b` |
| `ANTHROPIC_INSECURE_HTTP` | HTTP sin SSL | `1` |
| `NODE_TLS_REJECT_UNAUTHORIZED` | Certificados inválidos | `0` |
| `OLLAMA_HOST` | Evitar conflicto local | `` |

## 🔧 Desarrollo

### Entorno de Desarrollo

```bash
# Crear entorno virtual con uv
uv venv .venv

# Activar
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate.bat  # Windows

# Instalar en modo editable
pip install -e ".[dev]"

# O usar uv
uv pip install -e .
```

### Ejecutar sin Instalar

```bash
# Directamente desde código fuente
python -m claude_launch.main mole --model mistral:latest

# Con provider específico
python -m claude_launch.main chati --model qwen3.5:35b
```

## 📦 Compilación a Binary

### build.sh (Linux/macOS)

```bash
#!/bin/bash
set -e

echo "Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo "Compilando con PyInstaller..."
mkdir -p dist
pyinstaller --onefile --console --name ccl src/claude_launch/main.py

chmod +x dist/ccl
```

**Salida:** `dist/ccl`

### build.bat (Windows)

```batch
@echo off
setlocal enabledelayedexpansion

REM Usar Python del venv o system
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

REM Instalar dependencias
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt

REM Compilar con PyInstaller
%PYTHON_CMD% -m PyInstaller --clean ^
    --onefile ^
    --name=ccl ^
    --hidden-import=claude_launch.config ^
    --hidden-import=claude_launch.cli ^
    --hidden-import=claude_launch.ollama_api ^
    --hidden-import=claude_launch.launcher ^
    --hidden-import=rich ^
    --hidden-import=pydantic ^
    --console ^
    --noconfirm ^
    src/claude_launch/main.py
```

**Salida:** `dist/ccl.exe`

### cl.spec (PyInstaller Spec)

Archivo de especificación para builds Windows avanzados:

```python
a = Analysis(
    ['src\\claude_launch\\main.py'],
    pathex=[],
    hiddenimports=[
        'claude_launch.config',
        'claude_launch.cli',
        'claude_launch.ollama_api',
        'claude_launch.launcher',
        'rich',
        'pydantic'
    ],
    # ... más configuración
)
```

## 🧪 Testing y Verificación

```bash
# Verificar instalación
python -m claude_launch.main --help

# Probar provider con modelo específico
python -m claude_launch.main mole --model mistral:latest

# Listar providers configurados
python -m claude_launch.main --list

# Verificar que los módulos se importan correctamente
python -c "from claude_launch import ConfigWrapper, OllamaAPI, ClaudeLauncher; print('OK')"
```

## 📝 Contribuir

### Flujo de Trabajo

1. **Fork** el repositorio
2. **Crear rama**: `git checkout -b feature/nueva-caracteristica`
3. **Hacer cambios** en `src/claude_launch/`
4. **Probar localmente**: `python -m claude_launch.main`
5. **Commit** con mensajes descriptivos
6. **Pull Request**

### Buenas Prácticas

- Nombres de variables en snake_case
- Type hints para todas las funciones
- Docstrings en componentes públicos
- Manejo graceful de errores en API calls
- Validación con pydantic para config

## 🔍 Depuración

Habilitar debug:

```bash
# Ver logs de conexión
export PYTHONDEBUG=1
python -m claude_launch.main mole --model mistral:latest
```

Ver logs del launcher:

```python
from claude_launch.launcher import ClaudeLauncher
import logging

logging.basicConfig(level=logging.DEBUG)
launcher = ClaudeLauncher(...)
```

## 📄 Licencia

MIT License - ver archivo `LICENSE`.
