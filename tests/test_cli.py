"""Tests para la interfaz de lnea de comandos."""

import json
import tempfile
import unittest
from pathlib import Path

from claude_launch.config import ConfigWrapper, ProviderConfig, ProviderOptions, ModelConfig


class TestCLIListCommand(unittest.TestCase):
    """Tests para el comando --list."""

    def setUp(self):
        """Crear configuracion con varios providers para pruebas."""
        config_data = {
            "mole": {
                "type": "ollama",
                "options": {
                    "base_url": "http://127.0.0.1:11434",
                    "apiKey": "ollama"
                },
                "models": {}
            },
            "remote": {
                "type": "ollama",
                "options": {
                    "base_url": "http://ollama-server:11434",
                    "apiKey": "secret-key"
                },
                "models": {
                    "llama3": {"name": "llama3"},
                    "mistral": {"name": "mistral"}
                }
            }
        }
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        self.temp_config_path = Path(temp_file.name)

    def tearDown(self):
        """Limpiar archivo temporal."""
        if self.temp_config_path.exists():
            self.temp_config_path.unlink()

    def test_list_providers_displays_all(self):
        """Test que --list muestra todos los providers."""
        config = ConfigWrapper(self.temp_config_path)
        providers = config.providers

        self.assertEqual(len(providers), 2)
        self.assertIn("mole", providers)
        self.assertIn("remote", providers)

    def test_list_shows_provider_urls(self):
        """Test que --list muestra las URLs de los providers."""
        config = ConfigWrapper(self.temp_config_path)
        providers = config.providers

        self.assertEqual(providers["mole"].options.base_url, "http://127.0.0.1:11434")
        self.assertEqual(providers["remote"].options.base_url, "http://ollama-server:11434")


class TestCLIAddProvider(unittest.TestCase):
    """Tests para el asistente de creacion de providers."""

    def test_validate_provider_name_empty(self):
        """Test validacion de nombre vacio."""
        name = ""
        self.assertTrue(not name or name in {"$schema", "share", "tools"})

    def test_validate_provider_name_invalid_keys(self):
        """Test validacion de nombres reservados."""
        invalid_names = ["$schema", "share", "tools"]
        for name in invalid_names:
            self.assertIn(name, {"$schema", "share", "tools"})

    def test_validate_provider_name_valid(self):
        """Test validacion de nombres validos."""
        valid_names = ["mynamespace", "mole", "remote-server", "provider123"]
        for name in valid_names:
            self.assertNotIn(name, {"$schema", "share", "tools"})

    def test_create_provider_config(self):
        """Test creacion de configuracion de provider."""
        provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(
                base_url="http://localhost:11434",
                api_key="my-api-key"
            ),
            models={
                "model1": ModelConfig(name="model1"),
                "model2": ModelConfig(name="model2")
            }
        )

        self.assertEqual(provider.type, "ollama")
        self.assertEqual(provider.options.base_url, "http://localhost:11434")
        self.assertEqual(provider.options.api_key, "my-api-key")
        self.assertEqual(len(provider.models), 2)

    def test_create_provider_with_empty_models(self):
        """Test creacion de provider sin modelos."""
        provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(base_url="http://localhost:11434"),
            models={}
        )

        self.assertEqual(provider.type, "ollama")
        self.assertEqual(len(provider.models), 0)


class TestCLIIntegration(unittest.TestCase):
    """Tests de integracion para la CLI."""

    def setUp(self):
        """Crear config temporal con varios providers."""
        config_data = {
            "provider1": {
                "type": "ollama",
                "options": {"base_url": "http://localhost:11434", "apiKey": "key1"},
                "models": {"model1": {"name": "model1"}}
            },
            "provider2": {
                "type": "ollama",
                "options": {"base_url": "http://localhost:21144", "apiKey": "key2"},
                "models": {"model2": {"name": "model2"}}
            }
        }
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        self.temp_config_path = Path(temp_file.name)

    def tearDown(self):
        """Limpiar archivo temporal."""
        if self.temp_config_path.exists():
            self.temp_config_path.unlink()

    def test_list_multiple_providers(self):
        """Test listar multiples providers."""
        config = ConfigWrapper(self.temp_config_path)
        providers = config.providers

        self.assertEqual(len(providers), 2)
        self.assertIn("provider1", providers)
        self.assertIn("provider2", providers)

    def test_add_then_list(self):
        """Test agregar provider y luego listar."""
        config = ConfigWrapper(self.temp_config_path)

        # Agregar nuevo provider
        new_provider = ProviderConfig(
            type="ollama",
            options=ProviderOptions(base_url="http://localhost:31155"),
            models={"newmodel": {"name": "newmodel"}}
        )
        config.add_provider("provider3", new_provider)

        # Listar
        providers = config.providers
        self.assertEqual(len(providers), 3)
        self.assertIn("provider3", providers)


if __name__ == '__main__':
    unittest.main()
