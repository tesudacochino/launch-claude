# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Launch** is a CLI launcher for Claude Code that supports multiple Ollama-based providers. It enables connecting Claude Code to various Ollama endpoints via the `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` environment variables, following the OpenCode-style configuration format.

## Key Commands

### Development Setup
```bash
# Full installation with uv (dependencies + config)
./install.sh all

# Install dependencies only
./install.sh install

# Run the CLI directly (after activation)
source .venv/bin/activate
python -m claude_launch.main [provider] [--model <name>]
```

### Running the CLI
```bash
# Mostrar help
./scripts/cl                           # Muestra help de uso
./scripts/cl --help                    # Muestra help de uso

# List models and select interactively
./scripts/cl mole
./scripts/cl chati

# Launch directly with a specific model
./scripts/cl mole --model mistral:latest
./scripts/cl chati --model qwen3.5:122b

# Add a new provider via interactive assistant
./scripts/cl --new

# Use custom config file
./scripts/cl --config /path/to/config.json [provider]

# Pass flags directly to Claude Code (after --)
./scripts/cl mole --model mistral:latest -- --dangerously-skip-permissions
./scripts/cl mole --model qwen3.5:122b -- --verbose --timeout=60
```

### Build and Compilation
```bash
# Compile to binary using Nuitka (requires nuitka installed)
./build.sh auto      # Auto-detect platform
./build.sh linux     # Linux/macOS binary
./build.sh windows   # Windows cross-compilation

# Output: 'cl' or 'cl.exe' single-file executable
```

### Testing and Linting
- No formal test suite exists yet
- Run via: `python -m claude_launch.main --help` to verify CLI works
- Dependencies are managed via `pyproject.toml` with hatchling build system

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
│   ├── cl                  # Linux/macOS wrapper script
│   └── cl.bat              # Windows batch wrapper
├── install.sh              # Installation script using uv
└── build.sh                # Binary compilation script using Nuitka
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
- Injects `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` per-provider
- Supports optional `--model` argument passing to Claude Code CLI

## Configuration Format

Providers are stored directly at the root of `config.json`:

```json
{
  "mole": {
    "type": "ollama",
    "name": "mole",
    "options": {
      "baseURL": "http://127.0.0.1:11434/v1",
      "apiKey": "ollama"
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
- `baseURL` derives the provider identifier from hostname
- Models dict allows pre-specifying available models (optional - can be fetched at runtime)

## File Structure Notes

- Package imports use `.claude_launch.*` relative syntax (e.g., `from .config import ConfigWrapper`)
- Virtual environment at `.venv/` created via `uv venv .venv`
- Binary builds output to repo root as single-file executables (`cl` or `cl.exe`)

## Development Workflow

1. **Modify code**: Edit files under `src/claude_launch/`
2. **Test locally**: Activate venv and run `python -m claude_launch.main [args]`
3. **Add provider**: Use `./scripts/cl --new` or edit `config.json` directly
4. **Build binary**: Run `./build.sh auto` to compile standalone executable
