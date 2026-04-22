# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Launch** (CLI command: `ccl`) is a launcher for Claude Code that supports multiple Ollama-based providers. It uses `config.json` in OpenCode format to manage providers with base URLs and API keys.

Configuration follows an OpenCode-style format where providers are stored directly at the root level of `config.json`.

## Key Commands

### Development Setup
```bash
# Install in editable mode
pip install -e .

# Or with uv
uv pip install -e .

# Run CLI directly
python -m claude_launch.main [provider] [--model <name>]
```

### Running the CLI
```bash
# Show help
ccl
ccl --help

# List models interactively for a provider
ccl mole
ccl chati

# Launch directly with a specific model
ccl mole --model mistral:latest
ccl chati --model qwen3.5:35b

# Launch without asking for permissions (-d shortcut)
ccl mole --model mistral:latest -d

# Add a new provider via interactive assistant
ccl --new

# List all configured providers
ccl --list
ccl -l

# Remove a provider
ccl --remove <provider>
ccl -r <provider>

# Use custom config file
ccl --config /path/to/config.json [provider]

# Pass flags to Claude Code (after --)
ccl mole --model qwen3.5:35b -- --verbose --timeout=60
```

### Build and Compilation

Binaries are built automatically via GitHub Actions on tag push (`v*`). For local builds:

```bash
pip install -e '.[build]'
python -m PyInstaller --clean ccl.spec --noconfirm
# Output: dist/ccl (Linux/macOS) or dist/ccl.exe (Windows)
```

### Testing and Linting
- No formal test suite exists yet
- Verify CLI works: `python -m claude_launch.main --help`
- Dependencies managed via `pyproject.toml` with hatchling
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
├── ccl.spec                # PyInstaller spec for binary builds
├── config.json             # Provider configurations (OpenCode-style format)
├── .github/workflows/
│   └── release.yml         # CI/CD: builds binaries on tag push
├── src/claude_launch/      # Main Python package
│   ├── __init__.py         # Exports: Config, ProviderConfig, OllamaAPI, ClaudeLauncher
│   ├── main.py             # CLI entry point with argparse
│   ├── config.py           # Configuration management (pydantic + OpenCode wrapper)
│   ├── cli.py              # Rich-based interactive UI (menus, selection, prompts)
│   ├── console.py          # Shared rich.Console singleton instance
│   ├── ollama_api.py       # Ollama API client for model listing and connection testing
│   ├── launcher.py         # Subprocess launcher for Claude Code with env vars
│   └── _commit.py          # Auto-generated commit hash (used in binary builds)
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
- `-d` / `--dangerously-skip-permissions`: shortcut that injects the flag into Claude Code
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
- `-d` / `--dangerously-skip-permissions` en main.py inyecta el flag automáticamente en extra_args

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
- Entry point defined in `pyproject.toml`: `ccl = "claude_launch.main:main"`
- Binary builds output to `dist/ccl` (Linux/macOS) or `dist/ccl.exe` (Windows)
- `config.json` location: same directory as executable when run as binary

## Development Workflow

1. **Modify code**: Edit files under `src/claude_launch/`
2. **Test locally**: Run `python -m claude_launch.main [args]` or `ccl [args]`
3. **Add provider**: Use `ccl --new` or edit `config.json` directly
4. **Release**: Push a `v*` tag to trigger CI binary builds

## Notes

- `ccl.spec` is the PyInstaller spec file used for binary builds (defines hidden imports, commit hash injection)
- Configuration is loaded from `config.json` in the same directory as the executable when running as a binary
- Default `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` are set to the selected model
