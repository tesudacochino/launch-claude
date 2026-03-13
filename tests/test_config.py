"""Tests para la gestion de configuracion y providers."""

import json
import tempfile
import unittest
from pathlib import Path

from claude_launch.config import ConfigWrapper, ProviderConfig, ProviderOptions, ModelConfig


class TestProviderOptions(unittest.TestCase):
    """Tests para ProviderOptions."""

    def test_default_api_key(self):
        """Test que la API key por defecto es 'ollama'."""
        options = ProviderOptions(base_url="http://localhost:11434")
        self.assertEqual(options.api_key, "ollama")

    def test_custom_api_key(self):
        """Test que se puede configurar una API key personalizada."""
        options = ProviderOptions(base_url="http://localhost:11434", api_key="my-key")
        self.assertEqual(options.api_key, "my-key")

    def test_to_env_vars(self):
        """Test conversion a variables de entorno."""
        options = ProviderOptions(base_url="http://localhost:11434", api_key="test-key")
        env_vars = options.to_env_vars()
        self.assertEqual(env_vars["ANTHROPIC_BASE_URL"], "http://localhost:11434")
        self.assertEqual(env_vars["ANTHROPIC_API_KEY"], "test-key")


class TestProviderConfig(unittest.TestCase):
    """Tests para ProviderConfig."""

    def test_provider_name_from_url(self):
        """Test que el nombre se extrae correctamente de la URL."""
        provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(base_url="http://localhost:11434")
        )
        self.assertEqual(provider.name, "localhost:11434")

    def test_provider_with_models(self):
        """Test provider con modelos configurados."""
        provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(base_url="http://localhost:11434"),
            models={
                "claude-3.5-sonnet": ModelConfig(name="claude-3.5-sonnet"),
                "claude-3-haiku": ModelConfig(name="claude-3-haiku")
            }
        )
        self.assertEqual(len(provider.models), 2)
        self.assertIn("claude-3.5-sonnet", provider.models)


def create_temp_config_file(config_data: dict) -> Path:
    """Crear un archivo de configuracion temporal para pruebas."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(config_data, temp_file)
    temp_file.close()
    return Path(temp_file.name)


class TestConfigWrapper(unittest.TestCase):
    """Tests para ConfigWrapper."""

    def setUp(self):
        """Crear archivo de configuracion temporal."""
        config_data = {
            "mole": {
                "type": "ollama",
                "options": {
                    "base_url": "http://127.0.0.1:11434",
                    "apiKey": "ollama"
                },
                "models": {}
            }
        }
        self.temp_config_path = create_temp_config_file(config_data)

    def tearDown(self):
        """Limpiar archivo temporal."""
        if self.temp_config_path.exists():
            self.temp_config_path.unlink()

    def test_load_providers(self):
        """Test cargar providers desde archivo."""
        config = ConfigWrapper(self.temp_config_path)
        providers = config.providers
        self.assertIn("mole", providers)
        self.assertEqual(providers["mole"].options.base_url, "http://127.0.0.1:11434")

    def test_list_providers(self):
        """Test listar nombres de providers."""
        config = ConfigWrapper(self.temp_config_path)
        provider_names = list(config.providers.keys())
        self.assertIn("mole", provider_names)

    def test_add_provider(self):
        """Test agregar un nuevo provider."""
        config = ConfigWrapper(self.temp_config_path)

        new_provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(
                base_url="http://localhost:21144",
                api_key="test-key"
            ),
            models={
                "test-model": ModelConfig(name="test-model")
            }
        )

        config.add_provider("test", new_provider)

        # Verificar que se agrego
        self.assertIn("test", config.providers)
        self.assertEqual(config.providers["test"].options.base_url, "http://localhost:21144")

    def test_remove_provider(self):
        """Test eliminar un provider."""
        config = ConfigWrapper(self.temp_config_path)

        # Verificar que existe
        self.assertIn("mole", config.providers)

        # Eliminar
        result = config.remove_provider("mole")
        self.assertTrue(result)

        # Verificar que se elimino
        self.assertNotIn("mole", config.providers)


class TestEmptyConfig(unittest.TestCase):
    """Tests para configuracion vacia."""

    def setUp(self):
        """Crear archivo de configuracion vacio para pruebas."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump({}, temp_file)
        temp_file.close()
        self.temp_config_path = Path(temp_file.name)

    def tearDown(self):
        """Limpiar archivo temporal."""
        if self.temp_config_path.exists():
            self.temp_config_path.unlink()

    def test_empty_providers_list(self):
        """Test que un config vacio devuelve lista vacia."""
        config = ConfigWrapper(self.temp_config_path)
        self.assertEqual(len(config.providers), 0)

    def test_add_to_empty_config(self):
        """Test agregar provider a config vacio."""
        config = ConfigWrapper(self.temp_config_path)

        new_provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(base_url="http://localhost:11434"),
            models={}
        )

        config.add_provider("first", new_provider)
        self.assertIn("first", config.providers)


if __name__ == '__main__':
    unittest.main()
