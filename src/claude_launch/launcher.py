"""Lanzador de Claude Code con configuración específica."""

import os
import signal
import subprocess
import sys
import shutil
from typing import Optional


class ClaudeLauncher:
    """Ejecuta Claude Code con variables de entorno específicas."""

    def __init__(self, base_url: str, api_key: str = "ollama", model: str = "",
                 extra_args: Optional[list[str]] = None):
        """Inicializar el launcher.

        Args:
            base_url: URL del endpoint para Claude Code
            api_key: API key de autenticación
            model: Modelo a usar (ej: qwen3.5:35b)
            extra_args: Lista de flags adicionales a pasar a Claude Code (ej: ["--verbose", "--dangerously-skip-permissions"])
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.extra_args = extra_args or []

    def get_env_vars(self) -> dict[str, str]:
        """Obtener variables de entorno para lanzar Claude Code.

        Returns:
            Diccionario con TODAS las vars necesarias para Claude Code
        """
        return {
            "ANTHROPIC_BASE_URL": self.base_url,
            "ANTHROPIC_AUTH_TOKEN": self.api_key,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": self.model,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": self.model,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": self.model,
            "ANTHROPIC_INSECURE_HTTP": "1",
            "NODE_TLS_REJECT_UNAUTHORIZED": "0",
            "OLLAMA_HOST": "",
        }

    @staticmethod
    def _check_claude_installed() -> bool:
        """Verificar si el comando 'claude' está instalado en el PATH.

        Returns:
            True si claude está disponible, False en caso contrario
        """
        return shutil.which("claude") is not None

    def _signal_handler(self, signum, frame):
        """Manejar señales de interrupción (Ctrl+C, etc.)."""
        print("\n\n[interrupción por el usuario]")
        sys.exit(0)

    def launch(self, model: Optional[str] = None) -> subprocess.Popen:
        """Lanzar Claude Code con la configuración actual.

        Args:
            model: Nombre del modelo opcional (override)

        Returns:
            Proceso de Claude Code en ejecución

        Raises:
            RuntimeError: Si el comando 'claude' no está instalado
        """
        # Usar el modelo pasado o el configurado
        selected_model = model or self.model

        # Verificar que 'claude' está instalado
        if not self._check_claude_installed():
            raise RuntimeError(
                "El comando 'claude' no está instalado.\n\n"
                "Para usar Claude Launch necesitas instalar Claude Code:\n"
                "  - Visita: https://claude.ai/download\n"
                "  - O sigue las instrucciones de instalación en la documentación"
            )

        # Construir el comando
        cmd = ["claude"]
        cmd.extend(self.extra_args)

        # Registrar manejador de señales para Ctrl+C limpio
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Crear entorno específico SIN modificar os.environ global
        env = {**os.environ, **self.get_env_vars()}

        # Lanzar el proceso con el entorno específico
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env,
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
