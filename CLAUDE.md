# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Launch** (CLI command: `ccl`) is a launcher for Claude Code that supports multiple Ollama-based providers. It connects Claude Code to various Ollama-compatible endpoints using the `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` environment variables.

Configuration follows an OpenCode-style format where providers are stored directly at the root level of `config.json`.

## Key Commands

### Development Setup
```bash
# Linux/macOS - Install dependencies
./install.sh

# Windows - Install dependencies
install.bat

# Run CLI directly (from venv)
source .venv/bin/activate
python -m claude_launch.main [provider] [--model <name>]
```

### Running the CLI
```bash
# Show help
./scripts/ccl
./scripts/ccl --help

# List models interactively for a provider
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

# Pass flags to Claude Code (after --)
./scripts/ccl mole --model mistral:latest -- --dangerously-skip-permissions
./scripts/ccl mole --model qwen3.5:35b -- --verbose --timeout=60
```

### Build and Compilation

**Linux/macOS:**
```bash
./build.sh
# Output: dist/ccl
```

**Windows:**
```powershell
build.bat
# Output: dist/ccl.exe
```

**Note:** Requires PyInstaller installed (`pip install pyinstaller`)

### Testing and Linting
- No formal test suite exists yet
- Verify CLI works: `python -m claude_launch.main --help`
- Dependencies are managed via `pyproject.toml` with hatchling build system
- No linting or pre-commit hooks configured

## Environment Variables

When launching Claude Code, the launcher sets these environment variables:
- `ANTHROPIC_BASE_URL`: Ollama endpoint URL (e.g., `http://127.0.0.1:11434/v1`)
- `ANTHROPIC_AUTH_TOKEN`: API key for authentication (e.g., `ollama`)
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`: Default model for Haiku
- `ANTHROPIC_DEFAULT_OPUS_MODEL`: Default model for Opus
- `ANTHROPIC_DEFAULT_SONNET_MODEL`: Default model for Sonnet
- `ANTHROPIC_INSECURE_HTTP`: `"1"` - enables HTTP without SSL verification
- `NODE_TLS_REJECT_UNAUTHORIZED`: `"0"` - accepts invalid certificates
- `OLLAMA_HOST`: `""` - avoids conflicts with local Ollama

## High-Level Architecture

```
claude-launch/
├── pyproject.toml          # Project metadata, dependencies, hatch build config
├── config.json             # Provider configurations (OpenCode-style format)
├── src/claude_launch/      # Main Python package
│   ├── __init__.py         # Exports: Config, ProviderConfig, OllamaAPI, ClaudeLauncher
│   ├── main.py             # CLI entry point with argparse
│   ├── config.py           # Configuration management (pydantic + OpenCode wrapper)
│   ├── cli.py              # Rich-based interactive UI (menus, selection, prompts)
│   ├── ollama_api.py       # Ollama API client for model listing and connection testing
│   └── launcher.py         # Subprocess launcher for Claude Code with env vars
├── scripts/                # CLI wrappers
│   ├── ccl                  # Linux/macOS wrapper script
│   └── ccl.bat              # Windows batch wrapper
├── install.sh              # Linux/macOS installation script
├── install.bat             # Windows installation script (uses uv)
├── build.sh                # Linux/macOS binary compilation (PyInstaller)
├── build.bat               # Windows binary compilation (PyInstaller)
├── cl.spec                 # PyInstaller spec file for Windows builds
```

## Core Components

### Configuration System (`config.py`)
- **OpenCode-style format**: Providers stored at root level in `config.json`, not under a `providers` key
- `ConfigWrapper`: Parses OpenCode format, filters metadata keys (`$schema`, `share`, `tools`)
- `ProviderConfig`: Defines type, options (`base_url`, `api_key`), and available models
- `ProviderOptions`: Pydantic model for connection options with `base_url` and `api_key`
- Provider names are derived from `config.json` keys (e.g., `"mole"`, `"chati"`)
- Supports both `base_url`/`baseURL` and `api_key`/`apiKey` for flexibility

### CLI Interface (`cli.py` + `main.py`)
- Uses `rich` for terminal UI (tables, panels, prompts)
- `main.py`: argparse-based argument parsing, mode dispatching
- `cli.py`: Interactive menus for provider/model selection and adding new providers
- Modes: interactive model selection, direct model launch, provider addition wizard
- Extra args after `--` are passed through to Claude Code

### API Client (`ollama_api.py`)
- `OllamaAPI` class wraps OpenAI-compatible Ollama endpoints
- Methods: `list_models()`, `check_model_exists()`, `test_connection()`
- Handles OpenAI format (`{"data": [...]}`), native Ollama format (`["model1", ...]`), and `{"models": [...]}`
- Graceful connection error handling

### Launcher (`launcher.py`)
- `ClaudeLauncher` sets up environment variables and spawns Claude Code subprocess
- Injects `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` per-provider
- Also sets `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`
- Supports optional `--model` argument and extra args passed to Claude Code CLI
- `--dangerously-skip-permissions` flag is passed through to Claude Code

## Configuration Format

Providers are stored directly at the root of `config.json` (OpenCode-style):

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

**Key points:**
- Provider name is the JSON key (e.g., `"mole"`)
- `base_url`/`baseURL` and `api_key`/`apiKey` are both supported
- `models` dict is optional - fetched at runtime via API

## File Structure Notes

- Package imports use `.claude_launch.*` relative syntax (e.g., `from .config import ConfigWrapper`)
- Virtual environment at `.venv/` created via `uv venv .venv`
- Binary builds output to `dist/ccl` (Linux/macOS) or `dist/ccl.exe` (Windows)
- `config.json` location: same directory as executable when run as binary

## Development Workflow

1. **Modify code**: Edit files under `src/claude_launch/`
2. **Test locally**: Activate venv and run `python -m claude_launch.main [args]`
3. **Add provider**: Use `./scripts/ccl --new` or edit `config.json` directly
4. **Build binary**: Run `./build.sh` to compile standalone executable

## Notes

- `install.sh` uses `pip` for dependency installation from `pyproject.toml`
- `install.bat` uses `uv` (requires `uv` installed separately) for cross-platform consistency
- `build.sh` (Linux/macOS) and `build.bat` (Windows) use PyInstaller for binary compilation
- `cl.spec` is the PyInstaller spec file used for Windows builds (defines hidden imports)
- Configuration is loaded from `config.json` in the same directory as the executable when running as a binary
- On Windows, `scripts/ccl.bat` handles UTF-8 encoding for emojis and special characters
- Default `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` are set to the selected model

## Related Documentation

- [README.md](./README.md) - User-facing documentation with quick start and usage examples
- [DOCUMENTACION_TECNICA.md](./DOCUMENTACION_TECNICA.md) - Technical documentation for developers (architecture, build process, API details)
