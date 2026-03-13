"""Lanzador de Claude Code con configuración específica."""

import os
import subprocess
import sys
from typing import Optional


class ClaudeLauncher:
    """Ejecuta Claude Code con variables de entorno específicas."""

    def __init__(self, base_url: str, api_key: str = "ollama", model: str = "qwen3.5:35b"):
        """Inicializar el launcher.

        Args:
            base_url: URL del endpoint para Claude Code
            api_key: API key de autenticación
            model: Modelo por defecto (ej: qwen3.5:35b)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def get_env_vars(self) -> dict[str, str]:
        """Obtener variables de entorno para lanzar Claude Code."""
        return {
            **os.environ.copy(),
            # Variables del servidor
            "ANTHROPIC_BASE_URL": self.base_url,
            "ANTHROPIC_AUTH_TOKEN": self.api_key,
            # Modelos Anthropic -> Ollama
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": self.model or "qwen3.5:35b",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": self.model or "qwen3.5:35b",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": self.model or "qwen3.5:35b",
            # Certificados internos
            "ANTHROPIC_INSECURE_HTTP": "1",
            "NODE_TLS_REJECT_UNAUTHORIZED": "0",
            # Evitar conflictos con Ollama local
            "OLLAMA_HOST": "",
        }

    def launch(self, model: Optional[str] = None) -> subprocess.Popen:
        """Lanzar Claude Code con la configuración actual.

        Args:
            model: Nombre del modelo opcional (ej: qwen3.5:35b)

        Returns:
            Proceso de Claude Code en ejecución
        """
        # Usar el modelo pasado o el configurado
        selected_model = model or self.model

        # Fijar las variables de entorno en el proceso actual ANTES de lanzar Claude
        os.environ["ANTHROPIC_BASE_URL"] = self.base_url
        os.environ["ANTHROPIC_AUTH_TOKEN"] = self.api_key
        os.environ["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = selected_model
        os.environ["ANTHROPIC_DEFAULT_OPUS_MODEL"] = selected_model
        os.environ["ANTHROPIC_DEFAULT_SONNET_MODEL"] = selected_model
        os.environ["ANTHROPIC_INSECURE_HTTP"] = "1"
        os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
        os.environ["OLLAMA_HOST"] = ""

        # Construir el comando - usa el ejecutable claude que está en el PATH
        cmd = ["claude"]

        # Lanzar el proceso heredando las variables de entorno ya configuradas
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        return process

    def launch_interactive(self, model: Optional[str] = None) -> int:
        """Lanzar Claude Code y esperar a que termine (modo interactivo).

        Args:
            model: Nombre del modelo opcional

        Returns:
            Código de salida del proceso
        """
        process = self.launch(model)
        return process.wait()
