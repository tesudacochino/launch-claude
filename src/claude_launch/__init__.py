"""Claude Launch - Lanzador de Claude Code con múltiples providers Ollama."""

__version__ = "1.1.8"
__author__ = "Mole"

from .config import Config, ProviderConfig
from .ollama_api import OllamaAPI
from .launcher import ClaudeLauncher

__all__ = [
    "Config",
    "ProviderConfig",
    "OllamaAPI",
    "ClaudeLauncher",
]
