"""Interfaz de línea de comandos con menús interactivos."""

import sys
from typing import Optional, Union
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.box import SIMPLE
from rich.layout import Layout
from rich.live import Live

from claude_launch.config import ConfigWrapper, ProviderConfig
from claude_launch.ollama_api import OllamaAPI
from claude_launch.launcher import ClaudeLauncher


console = Console()


def show_main_menu(config: ConfigWrapper):
    """Mostrar menú principal con todos los providers."""
    from rich.panel import Panel

    providers = config.providers

    if not providers:
        console.print(
            Panel(
                "No hay providers configurados.\n\n"
                "Ejecuta [bold]cl --new[/bold] para agregar uno nuevo.",
                title="Sin Providers",
                border_style="yellow"
            )
        )
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=3)
    table.add_column("Provider", style="blue")
    table.add_column("URL", style="green")

    for idx, (name, provider) in enumerate(sorted(providers.items()), 1):
        table.add_row(
            str(idx),
            name.capitalize(),
            provider.options.base_url.split(":")[0]
        )

    console.print()
    console.print(Panel(table, title="Claude Launch - Providers Disponibles"))
    console.print("\n[bold]Opciones:[/bold]")
    console.print("  [cyan]cl [provider][/cyan]     - Ver modelos de un provider")
    console.print("  [cyan]cl --new[/cyan]            - Agregar nuevo provider")
    console.print("  [cyan]cl --exit[/cyan]           - Salir")


def show_provider_models(provider: ProviderConfig):
    """Mostrar modelos disponibles de un provider en una tabla numerada."""
    try:
        ollama_api = OllamaAPI(
            provider.options.base_url,
            provider.options.api_key
        )
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


def select_model(provider: ProviderConfig) -> Optional[str]:
    """Permitir al usuario seleccionar un modelo.

    Returns:
        Nombre del modelo seleccionado o None si se cancela
    """
    try:
        ollama_api = OllamaAPI(
            provider.options.base_url,
            provider.options.api_key
        )
        available_models = ollama_api.list_models()
    except ConnectionError:
        console.print("\n[red]ERROR: No se pudieron cargar los modelos del provider.[/red]")
        console.print("Verifica que Ollama esté corriendo y sea accesible.")
        return None

    if not available_models:
        console.print("\n[red]ERROR: No hay modelos disponibles.[/red]")
        return None

    # Usar la lista ya mostrada por show_provider_models, no repetirla
    # Mostrar solo la solicitud de selección
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


def add_provider_interactively():
    """Asistente interactivo para agregar un nuevo provider."""
    console.print("\n[bold]Nuevo Provider[/bold]\n")

    # Nombre del provider
    name = Prompt.ask(
        "Nombre del provider",
        default="mynamespace"
    )

    if not name or name in {"$schema", "share", "tools"}:
        console.print("[yellow]WARNING: Nombre inválido.[/yellow]")
        return False

    # URL base
    while True:
        base_url = Prompt.ask(
            "URL base del endpoint",
            default="http://127.0.0.1:11434"
        )

        if not base_url:
            console.print("[red]ERROR: URL requerida.[/red]")
            continue

        # Probar conexión
        ollama_api = OllamaAPI(base_url)
        if ollama_api.test_connection():
            console.print(f"[green]OK: Conexión exitosa a {base_url}[/green]")
            break
        else:
            console.print(f"[red]ERROR: No se pudo conectar a {base_url}. Verifica que Ollama esté corriendo.[/red]")

    # API Key
    api_key = Prompt.ask(
        "API Key",
        default="ollama"
    )

    # Preguntar si tiene modelos específicos
    has_models = Confirm.ask(
        "\n¿Tienes una lista de modelos específicos?",
        default=True
    )

    models_dict = {}
    if has_models:
        console.print("\n[bold]Modelos disponibles:[/bold]")
        console.print("[dim]Puedes agregarlos luego manualmente en config.json[/dim]\n")

    # Configurar provider
    provider_config = ProviderConfig(
        type="ollama",
        options={"base_url": base_url, "apiKey": api_key},
        models=models_dict
    )

    return provider_config


def run_menu():
    """Ejecutar el menú interactivo principal."""
    from . import ConfigWrapper

    config = ConfigWrapper()

    try:
        while True:
            show_main_menu(config)

            choice = Prompt.ask(
                "\nOpción",
                choices=["1", "2", "3", "c"],
                default="exit"
            )

            if choice == "exit":
                console.print("\n[bold green]OK: Hasta luego![/bold green]")
                break
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")


def run_provider_selection(provider: ProviderConfig, dangerously_skip_permissions: bool = False,
                           extra_args: Optional[list[str]] = None):
    """Seleccionar un modelo y lanzar Claude Code.

    Args:
        provider: El provider seleccionado
        dangerously_skip_permissions: Si True, pasa --dangerously-skip-permissions a Claude Code
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
        show_provider_models(provider)

        # Seleccionar modelo
        model_name = select_model(provider)

        if not model_name:
            # console.print("[yellow]CANCELADO.[/yellow]")
            return

        # Verificar que el modelo existe
        if not ollama_api.check_model_exists(model_name):
            console.print(f"\n[red]ERROR: El modelo '{model_name}' no está disponible en este endpoint.[/red]")
            console.print("📋 Modelos disponibles:")
            for m in available_models:
                console.print(f"  • {m}")
            return

        # Lanzar Claude Code
        console.print(f"\n[bold green]OK: Llamando a Claude con modelo '{model_name}'...[/bold green]")

        # Construir flags adicionales para launch_interactive
        launcher_args = {}
        if dangerously_skip_permissions and "--dangerously-skip-permissions" not in (extra_args or []):
            launcher_args["extra_args"] = extra_args + ["--dangerously-skip-permissions"] if extra_args else ["--dangerously-skip-permissions"]
        else:
            launcher_args["extra_args"] = extra_args

        launcher = ClaudeLauncher(
            provider.options.base_url,
            provider.options.api_key,
            model=model_name,
            **launcher_args
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
        models={}  # models no se guarda, se fetchea en tiempo de ejecución
    )

    config.add_provider(name, provider_config)

    console.print(f"\n[bold green]✓ Provider '{name}' agregado exitosamente![/bold green]")
    console.print(f"📍 URL: {base_url}")
    console.print("[dim]Los modelos se cargarán automáticamente desde el provider[/dim]")
