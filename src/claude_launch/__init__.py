"""Claude Launch - Lanzador de Claude Code con múltiples providers Ollama."""

__version__ = "1.1.9"
__author__ = "Mole"

from .config import ConfigWrapper, ProviderConfig
from .ollama_api import OllamaAPI
from .launcher import ClaudeLauncher

__all__ = [
    "ConfigWrapper",
    "ProviderConfig",
    "OllamaAPI",
    "ClaudeLauncher",
]
