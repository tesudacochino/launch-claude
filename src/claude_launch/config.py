"""Manejo de configuración del launcher."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class ProviderOptions(BaseModel):
    """Opciones de conexión para un provider."""
    base_url: str = Field(..., description="URL base de la API")
    api_key: str = Field(default="ollama", description="API Key")


class ProviderConfig(BaseModel):
    """Configuración completa de un provider."""
    type: str = Field(default="ollama", description="Tipo de provider")
    options: ProviderOptions = Field(..., description="Opciones de conexión")
    models: dict[str, Any] = Field(
        default_factory=dict,
        description="Modelos disponibles"
    )


def _get_executable_path() -> Path:
    """Obtener la ruta del ejecutable (no del archivo temporal de PyInstaller)."""
    if hasattr(sys, '_MEIPASS') and sys._MEIPASS:
        # PyInstaller usa _MEIPASS para archivos extraídos
        return Path(sys.executable).parent
    # Ejecución con PyInstaller sin _MEIPASS o script congelado
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    # Ejecución normal desde script
    # Usar sys.executable para obtener la ruta correcta independientemente del cwd
    return Path(sys.executable).parent.resolve()


def _get_config_path() -> Path:
    """Obtener la ruta del archivo de configuración.

    El config.json debe estar en el mismo directorio que el ejecutable.
    Si no existe, se crea en ese lugar.

    Prioridad:
    1. config.json en el mismo directorio que el ejecutable (ccl.exe)
    2. ~/.claude/launch-config.json (fallback)
    """
    exe_path = _get_executable_path()

    # Primero: config.json en el directorio del ejecutable (mismo lugar que ccl.exe)
    exe_config = exe_path / "config.json"
    # Si no existe, lo creamos vacío para que el usuario pueda editar lo que necesite
    if not exe_config.exists():
        exe_config.parent.mkdir(parents=True, exist_ok=True)
        exe_config.write_text("{}\n")

    return exe_config.resolve()


class ConfigWrapper:
    """Wrapper para manejar la configuración tipo OpenCode."""

    def __init__(self, path: str | Path | None = None):
        """Inicializar con un archivo de configuración."""
        if path is None:
            path = _get_config_path()

        self.path = Path(path).resolve()
        self._data: dict[str, dict] = {}
        self._providers_cache: Optional[dict[str, ProviderConfig]] = None

        if self.path.exists():
            with open(self.path, "r") as f:
                data = json.load(f)
                # En config tipo OpenCode, los providers están en root
                # Filtramos las claves que son metadatos
                excluded_keys = {"$schema", "share", "tools"}
                self._data = {k: v for k, v in data.items() if k not in excluded_keys}
                # Parsear providers una vez en init
                self._providers_cache = self._parse_providers()

    @property
    def providers(self) -> dict[str, ProviderConfig]:
        """Obtener todos los providers (con cacheo)."""
        return self._providers_cache or {}

    def _parse_providers(self) -> dict[str, ProviderConfig]:
        """Parsear proveedores desde los datos raw."""
        providers: dict[str, ProviderConfig] = {}

        for name, data in self._data.items():
            # Si ya es un ProviderConfig, usar directamente
            if isinstance(data, ProviderConfig):
                providers[name] = data
                continue

            options_data = data.get("options", {})
            # Soportar ambos formatos: base_url y baseURL
            base_url = options_data.get("base_url") or options_data.get("baseURL", "")
            api_key = options_data.get("apiKey") or options_data.get("api_key", "ollama")
            # No cargar modelos desde config.json - se fetchearán desde la API en tiempo de ejecución

            providers[name] = ProviderConfig(
                type=data.get("type", "ollama"),
                options=ProviderOptions(base_url=base_url, api_key=api_key),
                models={},
            )

        return providers

    def invalidate_providers_cache(self) -> None:
        """Invalidar cache de providers después de agregar/eliminar providers."""
        self._providers_cache = None
        self._providers_cache = self._parse_providers()

    def save(self) -> None:
        """Guardar la configuración actual."""
        data = {}
        for name, provider in self._data.items():
            # Provider puede ser dict o ProviderConfig
            if hasattr(provider, 'model_dump'):
                data[name] = provider.model_dump()
            else:
                data[name] = provider

        # Reconstruir datos que queremos mantener
        if self.path.exists():
            with open(self.path, "r") as f:
                original = json.load(f)
            for key in ["$schema", "share", "tools"]:
                if key in original:
                    data[key] = original[key]

        # Asegurar que el directorio existe
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

        # Invalidar cache después de guardar
        self.invalidate_providers_cache()

    def add_provider(self, name: str, provider: ProviderConfig) -> None:
        """Agregar un nuevo provider."""
        self._data[name] = provider
        self.save()

    def remove_provider(self, name: str) -> bool:
        """Eliminar un provider."""
        if name in self._data and name not in {"$schema", "share", "tools"}:
            del self._data[name]
            self.save()
            return True
        return False
