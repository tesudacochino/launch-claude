# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Launch** is a CLI launcher for Claude Code that supports multiple Ollama-based providers. It enables connecting Claude Code to various Ollama endpoints via the `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` environment variables, following the OpenCode-style configuration format.

## Key Commands

### Development Setup
```bash
# Full installation (dependencies + config)
./install.sh all

# Install dependencies only
./install.sh install

# Run the CLI directly (after activation)
source .venv/bin/activate
python -m claude_launch.main [provider] [--model <name>]
```

### Running the CLI
```bash
# Show help
./scripts/ccl
./scripts/ccl --help

# List models and select interactively
./scripts/ccl mole
./scripts/ccl chati

# Launch directly with a specific model
./scripts/ccl mole --model mistral:latest
./scripts/ccl chati --model qwen3.5:35b

# Add a new provider via interactive assistant
./scripts/ccl --new

# List all configured providers
./scripts/ccl --list
./scripts/ccl -l

# Remove a provider
./scripts/ccl --remove <provider>
./scripts/ccl -r <provider>

# Use custom config file
./scripts/ccl --config /path/to/config.json [provider]

# Pass flags directly to Claude Code (after --)
./scripts/ccl mole --model mistral:latest -- --dangerously-skip-permissions
./scripts/ccl mole --model qwen3.5:35b -- --verbose --timeout=60
```

### Build and Compilation
```bash
# Compile to binary using PyInstaller (requires pyinstaller installed)
./build.sh

# Output: 'dist/ccl' or 'dist/ccl.exe' single-file executable
```

### Testing and Linting
- No formal test suite exists yet
- Run via: `python -m claude_launch.main --help` to verify CLI works
- Dependencies are managed via `pyproject.toml` with hatchling build system

## Environment Variables

When launching Claude Code, the following environment variables are set:
- `ANTHROPIC_BASE_URL`: URL del endpoint Ollama
- `ANTHROPIC_AUTH_TOKEN`: API key de autenticación
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`: Modelo por defecto para Haiku
- `ANTHROPIC_DEFAULT_OPUS_MODEL`: Modelo por defecto para Opus
- `ANTHROPIC_DEFAULT_SONNET_MODEL`: Modelo por defecto para Sonnet
- `ANTHROPIC_INSECURE_HTTP`: "1" (habilita HTTP sin SSL)
- `NODE_TLS_REJECT_UNAUTHORIZED`: "0" (acepta certificados no válidos)
- `OLLAMA_HOST`: "" (evita conflictos con Ollama local)

## High-Level Architecture

```
claude-launch/
├── pyproject.toml          # Project metadata, dependencies, hatch build config
├── config.json             # Provider configurations (OpenCode-style format)
├── src/claude_launch/      # Main Python package
│   ├── __init__.py         # Exports: Config, ProviderConfig, OllamaAPI, ClaudeLauncher
│   ├── main.py             # CLI entry point with argparse
│   ├── config.py           # Configuration management (pydantic models + OpenCode wrapper)
│   ├── cli.py              # Rich-based interactive UI (menus, selection, prompts)
│   ├── ollama_api.py       # Ollama API client for model listing and connection testing
│   └── launcher.py         # Subprocess launcher for Claude Code with env vars
├── scripts/                # CLI wrappers
│   ├── ccl                  # Linux/macOS wrapper script
│   └── ccl.bat              # Windows batch wrapper
├── install.sh              # Installation script using pip
└── build.sh                # Binary compilation script using PyInstaller
```

## Core Components

### Configuration System (`config.py`)
- **OpenCode-style format**: Providers at root level in `config.json`, not under a `providers` key
- `ConfigWrapper`: Parses OpenCode format, filters metadata keys (`$schema`, `share`, `tools`)
- `ProviderConfig`: Defines type, options (base_url, api_key), and available models
- Each provider exposes a unique name derived from the base URL hostname

### CLI Interface (`cli.py` + `main.py`)
- Uses `rich` for terminal UI (tables, panels, prompts)
- `main.py`: argparse-based argument parsing, mode dispatching
- `cli.py`: Interactive menus for provider/model selection and adding new providers
- Three modes: interactive model selection, direct model launch, provider addition wizard

### API Client (`ollama_api.py`)
- `OllamaAPI` class wraps OpenAI-compatible Ollama endpoints
- Methods: `list_models()`, `check_model_exists()`, `test_connection()`
- Handles connection errors gracefully, falls back to configured models

### Launcher (`launcher.py`)
- `ClaudeLauncher` sets up environment variables and spawns Claude Code subprocess
- Injects `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` per-provider
- Also sets `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`
- Supports optional `--model` argument passing to Claude Code CLI

## Configuration Format

Providers are stored directly at the root of `config.json`:

```json
{
  "mole": {
    "type": "ollama",
    "name": "localhost",
    "options": {
      "base_url": "http://127.0.0.1:11434/v1",
      "api_key": "ollama"
    },
    "models": {
      "mistral:latest": {"name": "mistral:latest"},
      "qwen3:32b": {"name": "qwen3:32b"}
    }
  }
}
```

Key points:
- Provider name is the JSON key (e.g., `"mole"`)
- `base_url` (snake_case) or `baseURL` (camelCase) are both supported
- `api_key` (snake_case), `apiKey` (camelCase) or `api_key` are both supported
- Models dict allows pre-specifying available models (optional - can be fetched at runtime)

## File Structure Notes

- Package imports use `.claude_launch.*` relative syntax (e.g., `from .config import ConfigWrapper`)
- Virtual environment at `.venv/` created via `uv venv .venv`
- Binary builds output to repo root as single-file executables (`ccl` or `ccl.exe`)

## Development Workflow

1. **Modify code**: Edit files under `src/claude_launch/`
2. **Test locally**: Activate venv and run `python -m claude_launch.main [args]`
3. **Add provider**: Use `./scripts/ccl --new` or edit `config.json` directly
4. **Build binary**: Run `./build.sh auto` to compile standalone executable

## Notes

- The `install.sh` script uses `pip` (not `uv`) for dependency installation
- The `build.sh` script compiles with PyInstaller to a single executable named `ccl` (or `ccl.exe` on Windows)
- Configuration is loaded from `config.json` in the same directory as the executable when running as a binary
