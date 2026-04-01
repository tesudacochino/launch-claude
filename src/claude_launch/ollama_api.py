"""Interfaz con la API de Ollama."""

import requests
from typing import Optional


class OllamaAPI:
    """Comunicación con el endpoint de Ollama."""

    def __init__(self, base_url: str, api_key: str = "ollama"):
        """Inicializar con URL base y API key.

        Args:
            base_url: URL del endpoint de Ollama (ej: http://127.0.0.1:11434/v1)
            api_key: API key para autenticación
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._model_cache: Optional[list[str]] = None

    @property
    def models(self) -> list[str]:
        """Obtener modelos disponibles con cacheo automático.

        La primera llamada hace HTTP GET, las siguientes usan cache en memoria.
        Usa invalidate_cache() para limpiar el cache.
        """
        if self._model_cache is None:
            self._model_cache = self._fetch_models()
        return self._model_cache

    def invalidate_cache(self) -> None:
        """Invalidar el cache de modelos (para cuando se agregan/eliminan modelos)."""
        self._model_cache = None

    def _fetch_models(self) -> list[str]:
        """Hacer la llamada HTTP real a la API de Ollama."""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()

            # Formato OpenAI compatible: {"data": [{"id": "..."}, ...]}
            if "data" in data and isinstance(data["data"], list):
                return [m["id"] for m in data["data"] if isinstance(m, dict) and "id" in m]

            # Formato Ollama nativo: ["model1", "model2", ...]
            if isinstance(data, list):
                return data

            # Otro formato posible: {"models": [{"name": "..."}, ...]}
            if "models" in data and isinstance(data["models"], list):
                return [m["name"] for m in data["models"] if isinstance(m, dict) and "name" in m]

            return []

        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.base_url}: {e}")

    def list_models(self) -> list[str]:
        """Listar todos los modelos disponibles en el endpoint.

        Returns:
            Lista de nombres de modelos disponibles
        """
        return self.models

    def check_model_exists(self, model_name: str) -> bool:
        """Verificar si un modelo específico existe.

        Args:
            model_name: Nombre del modelo a verificar

        Returns:
            True si el modelo existe, False en caso contrario
        """
        # Usa el cache existente - no hace HTTP adicional
        return model_name in self.models

    def test_connection(self) -> bool:
        """Probar si el endpoint es accesible.

        Returns:
            True si la conexión funciona, False en caso contrario
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
