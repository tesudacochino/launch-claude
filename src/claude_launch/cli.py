"""Interfaz de línea de comandos con menús interactivos."""

import sys
from typing import Optional
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.box import SIMPLE

from claude_launch.console import console
from claude_launch.config import ConfigWrapper, ProviderConfig
from claude_launch.ollama_api import OllamaAPI
from claude_launch.launcher import ClaudeLauncher


def show_provider_models(provider: ProviderConfig, ollama_api: OllamaAPI):
    """Mostrar modelos disponibles de un provider en una tabla numerada.

    Args:
        provider: El provider seleccionado
        ollama_api: Instancia ya creada de OllamaAPI (usa su list_models())
    """
    try:
        models = ollama_api.list_models()
    except ConnectionError as e:
        console.print(Panel(
            f"Error conectando con el endpoint:\n{e}",
            title="Error de Conexión",
            border_style="red"
        ))
        return

    if not models:
        console.print("\n[red]ERROR: No hay modelos disponibles.[/red]")
        return

    # Crear tabla numerada
    table = Table(show_header=False, box=SIMPLE)
    table.add_column("#", style="cyan", width=5)
    table.add_column("Modelo", style="white")

    for idx, model_name in enumerate(models, 1):
        table.add_row(str(idx), model_name)

    console.print(Panel(table, title="📦 Modelos Disponibles", border_style="green"))


def select_model(ollama_api: OllamaAPI) -> Optional[str]:
    """Permitir al usuario seleccionar un modelo.

    Args:
        ollama_api: Instancia de OllamaAPI (usa su cache de modelos)

    Returns:
        Nombre del modelo seleccionado o None si se cancela
    """
    available_models = ollama_api.models

    if not available_models:
        console.print("\n[red]ERROR: No hay modelos disponibles.[/red]")
        return None

    while True:
        try:
            choice = Prompt.ask(
                "\nSelecciona un modelo",
                default="cancel"
            )

            if choice.lower() == "cancel":
                return None

            try:
                idx = int(choice)
                if 1 <= idx <= len(available_models):
                    return available_models[idx - 1]
            except ValueError:
                pass

            console.print("[red]Selección inválida, intenta de nuevo.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelado.[/yellow]")
            return None


def run_provider_selection(provider: ProviderConfig,
                           extra_args: Optional[list[str]] = None):
    """Seleccionar un modelo y lanzar Claude Code.

    Args:
        provider: El provider seleccionado
        extra_args: Lista de flags adicionales a pasar a Claude Code
    """
    try:
        console.print(f"\n[bold]Conectando a {provider.options.base_url}...[/bold]")

        ollama_api = OllamaAPI(
            provider.options.base_url,
            provider.options.api_key
        )

        # Obtener modelos disponibles
        try:
            available_models = ollama_api.list_models()
        except ConnectionError as e:
            console.print(Panel(
                f"ERROR: No se pudo conectar al endpoint:\n{e}",
                title="Error de Conexión",
                border_style="red"
            ))
            console.print("[yellow]No se pueden cargar los modelos sin conexión al provider.[/yellow]")
            return

        if not available_models:
            console.print("[red]ERROR: No hay modelos disponibles.[/red]")
            return

        # Mostrar lista de modelos
        show_provider_models(provider, ollama_api)

        # Seleccionar modelo
        model_name = select_model(ollama_api)

        if not model_name:
            return

        # Lanzar Claude Code
        console.print(f"\n[bold green]OK: Llamando a Claude con modelo '{model_name}'...[/bold green]")

        launcher = ClaudeLauncher(
            provider.options.base_url,
            provider.options.api_key,
            model=model_name,
            extra_args=extra_args,
        )

        try:
            exit_code = launcher.launch_interactive()
            sys.exit(exit_code)
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelado por el usuario.[/yellow]")
            sys.exit(0)
        except RuntimeError as e:
            console.print(Panel(
                f"[red]ERROR:[/red] [bold]{e}[/bold]",
                title="Claude Code no instalado",
                border_style="red"
            ))
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
        sys.exit(0)


def run_new_provider():
    """Asistente para agregar un nuevo provider."""
    console.print("\n[bold blue]🔧 Configuración de Nuevo Provider[/bold blue]\n")

    config = ConfigWrapper()
    providers = config.providers

    # Nombre
    while True:
        name = Prompt.ask(
            "Nombre único del provider",
            default="mynamespace"
        )

        if not name:
            console.print("[red]ERROR: Nombre requerido.[/red]")
            continue

        if name in providers:
            console.print(f"[yellow]WARNING: '{name}' ya existe. Elige otro nombre.[/yellow]")
            continue

        break

    # URL base
    while True:
        base_url = Prompt.ask(
            "URL base del endpoint",
            default="http://127.0.0.1:11434"
        )

        if not base_url:
            console.print("[red]ERROR: URL requerida.[/red]")
            continue

        ollama_api = OllamaAPI(base_url)
        if ollama_api.test_connection():
            console.print(f"[green]OK: Conexión exitosa a {base_url}[/green]")
            break
        else:
            console.print(f"[red]ERROR: No se pudo conectar a {base_url}. Ollama no esta corriendo.[/red]")
            retry = Confirm.ask("\n[green]¿Intentar de nuevo?[/green]", default=True)
            if not retry:
                console.print("[yellow]Configuracion cancelada.[/yellow]")
                return False

    # API Key
    api_key = Prompt.ask(
        "API Key (dejalo en blanco para 'ollama')",
        default="ollama"
    )

    # Crear y guardar provider (sin modelos - se fetchearán desde API)
    provider_config = ProviderConfig(
        type="ollama",
        options={"base_url": base_url, "apiKey": api_key},
        models={}
    )

    config.add_provider(name, provider_config)

    console.print(f"\n[bold green]✓ Provider '{name}' agregado exitosamente![/bold green]")
    console.print(f"📍 URL: {base_url}")
    console.print("[dim]Los modelos se cargarán automáticamente desde el provider[/dim]")
