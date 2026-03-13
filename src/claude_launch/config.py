"""Manejo de configuración del launcher."""

import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class ProviderOptions(BaseModel):
    """Opciones de conexión para un provider."""
    base_url: str = Field(..., description="URL base de la API")
    api_key: str = Field(default="ollama", description="API Key")

    def to_env_vars(self) -> dict[str, str]:
        """Convertir a variables de entorno para Claude Code."""
        return {
            "ANTHROPIC_BASE_URL": self.base_url,
            "ANTHROPIC_API_KEY": self.api_key,
        }


class ModelConfig(BaseModel):
    """Configuración de un modelo específico."""
    name: str = Field(..., description="Nombre del modelo")

    def __str__(self) -> str:
        return self.name


class ProviderConfig(BaseModel):
    """Configuración completa de un provider."""
    type: str = Field(default="ollama", description="Tipo de provider")
    options: ProviderOptions = Field(..., description="Opciones de conexión")
    models: dict[str, ModelConfig] = Field(
        default_factory=dict,
        description="Modelos disponibles"
    )

    @property
    def name(self) -> str:
        """Nombre único del provider."""
        # Extraer el host:port de la URL
        url = self.options.base_url
        # Remover protocolo si existe
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        # Tomar la parte antes del primer /
        url = url.split("/")[0]
        return url


class Config(BaseModel):
    """Configuración principal con todos los providers."""
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._config_path: Path | None = kwargs.get("_config_path")

    @classmethod
    def load(cls, path: str | Path | None = None, _config_path: Path | None = None) -> "Config":
        """Cargar configuración desde un archivo JSON."""
        if path is None:
            # Buscar en posiciones comunes
            search_paths = [
                Path(__file__).parent.parent.parent / "config.json",
                Path.home() / ".claude" / "launch-config.json",
                Path("config.json"),
            ]
            for p in search_paths:
                if p.exists():
                    path = p
                    break

        if not path or not Path(path).exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        config_path = Path(path)
        with open(config_path, "r") as f:
            data = json.load(f)

        config = cls(**data, _config_path=config_path)
        return config

    def save(self) -> None:
        """Guardar configuración actual."""
        config_path = getattr(self, '_config_path', None)
        if not config_path:
            raise RuntimeError("No config path set")

        with open(config_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    def get_provider(self, name: str) -> ProviderConfig | None:
        """Obtener un provider por nombre."""
        # Buscar en providers del main config
        if hasattr(self, 'providers'):
            return self.providers.get(name)

        # En el caso de la estructura que usamos, los providers están en root
        # Esta es una workaround temporal hasta que refine el modelo
        return None

    def list_providers(self) -> list[str]:
        """Listar todos los nombres de providers."""
        if hasattr(self, 'providers'):
            return list(self.providers.keys())
        return []

    def add_provider(self, name: str, config: ProviderConfig) -> None:
        """Agregar un nuevo provider."""
        # En la estructura que usamos
        setattr(self, name, config)

    def remove_provider(self, name: str) -> bool:
        """Eliminar un provider."""
        if hasattr(self, name):
            delattr(self, name)
            return True
        return False

    @property
    def providers_dict(self) -> dict[str, ProviderConfig]:
        """Obtener todos los providers como diccionario."""
        # Para nuestro caso especial de OpenCode-style config
        return {}


class ConfigWrapper:
    """Wrapper para manejar la configuración tipo OpenCode."""

    def __init__(self, path: str | Path | None = None):
        """Inicializar con un archivo de configuración."""
        if path is None:
            search_paths = [
                Path("config.json"),
                Path.home() / ".claude" / "launch-config.json",
            ]
            for p in search_paths:
                if p.exists():
                    path = p
                    break

        self.path = Path(path) if path else Path("config.json")
        self._data: dict[str, dict] = {}

        if self.path.exists():
            with open(self.path, "r") as f:
                data = json.load(f)
                # En config tipo OpenCode, los providers están en root
                # Filtramos las claves que no son metadatos
                excluded_keys = {"$schema", "share", "tools"}
                self._data = {k: v for k, v in data.items() if k not in excluded_keys}

    @property
    def providers(self) -> dict[str, ProviderConfig]:
        """Obtener todos los providers."""
        return self._parse_providers()

    def _parse_providers(self) -> dict[str, ProviderConfig]:
        """Parsear proveedores desde los datos raw."""
        providers: dict[str, ProviderConfig] = {}

        for name, data in self._data.items():
            # Excluir keys que no son providers
            if name in {"$schema", "share", "tools"}:
                continue

            # Si ya es un ProviderConfig, usar directamente
            if isinstance(data, ProviderConfig):
                providers[name] = data
                continue

            options_data = data.get("options", {})
            # Soportar ambos formatos: base_url y baseURL
            base_url = options_data.get("base_url") or options_data.get("baseURL", "")
            api_key = options_data.get("apiKey") or options_data.get("api_key", "ollama")
            models = {
                model_name: ModelConfig(**model_data)
                for model_name, model_data in data.get("models", {}).items()
            }

            providers[name] = ProviderConfig(
                type=data.get("type", "ollama"),
                options=ProviderOptions(base_url=base_url, api_key=api_key),
                models=models,
            )

        return providers

    def save(self) -> None:
        """Guardar la configuración actual."""
        data = {}
        for name, provider in self._data.items():
            if name not in {"$schema", "share", "tools"}:
                # Provider puede ser dict o ProviderConfig
                if hasattr(provider, 'model_dump'):
                    data[name] = provider.model_dump()
                else:
                    data[name] = provider

        # Reconstruir datos que queremos mantener
        with open(self.path, "r") as f:
            original = json.load(f)

        for key in ["$schema", "share", "tools"]:
            if key in original:
                data[key] = original[key]

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

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
