"""Interfaz de línea de comandos con menús interactivos."""

import sys
from typing import Optional, Union
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
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
    table.add_column("Modelos", style="white")

    for idx, (name, provider) in enumerate(sorted(providers.items()), 1):
        models = ", ".join(m.name for m in provider.models.values()) if provider.models else "—"
        table.add_row(
            str(idx),
            name.capitalize(),
            provider.options.base_url.split(":")[0],
            f"[{len(provider.models)} modelos]" if models != "—" else "Sin especificar"
        )

    console.print()
    console.print(Panel(table, title="Claude Launch - Providers Disponibles"))
    console.print("\n[bold]Opciones:[/bold]")
    console.print("  [cyan]cl [provider][/cyan]     - Ver modelos de un provider")
    console.print("  [cyan]cl --new[/cyan]            - Agregar nuevo provider")
    console.print("  [cyan]cl --exit[/cyan]           - Salir")


def show_provider_models(provider: ProviderConfig):
    """Mostrar modelos disponibles de un provider."""
    models = list(provider.models.keys())

    if not models:
        # Intentar obtener desde API en tiempo real
        try:
            ollama_api = OllamaAPI(
                provider.options.base_url,
                provider.options.api_key
            )
            models = ollama_api.list_models()

            if models:
                console.print(
                    Panel(
                        "Modelos obtenidos desde API:\n" + "\n".join(f"  • {m}" for m in models),
                        title="📦 Modelos Disponibles",
                        border_style="green"
                    )
                )

        except ConnectionError as e:
            console.print(Panel(
                f"❌ Error conectando con el endpoint:\n{e}",
                title="Error de Conexión",
                border_style="red"
            ))
            models = []

    if not models:
        # Usar modelos configurados si no hay API
        models = list(provider.models.keys()) or ["(sin modelos especificados)"]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Modelo", style="white")

    for idx, model_name in enumerate(models, 1):
        table.add_row(str(idx), model_name)

    console.print(Panel(table, title=f"📦 Modelos de {provider.options.base_url}"))


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
        available_models = list(provider.models.keys()) or []

    if not available_models:
        console.print("\n[red]ERROR: No hay modelos disponibles.[/red]")
        return None

    # Mostrar opciones
    for idx, model in enumerate(available_models, 1):
        console.print(f"  [cyan]{idx}:[/cyan] {model}")

    while True:
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


def run_provider_selection(provider: ProviderConfig, dangerously_skip_permissions: bool = False,
                           extra_args: Optional[list[str]] = None):
    """Seleccionar un modelo y lanzar Claude Code.

    Args:
        provider: El provider seleccionado
        dangerously_skip_permissions: Si True, pasa --dangerously-skip-permissions a Claude Code
        extra_args: Lista de flags adicionales a pasar a Claude Code
    """
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
            f"WARNING: No se pudo conectar al endpoint:\n{e}\n\nUsando modelos configurados.",
            title="Advertencia",
            border_style="yellow"
        ))
        available_models = list(provider.models.keys())

    if not available_models:
        console.print("[red]ERROR: No hay modelos disponibles.[/red]")
        return

    # Mostrar lista de modelos
    show_provider_models(provider)

    # Seleccionar modelo
    model_name = select_model(provider)

    if not model_name:
        console.print("[yellow]CANCELADO.[/yellow]")
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

    exit_code = launcher.launch_interactive()
    sys.exit(exit_code)


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

    # Preguntar si hay modelos específicos
    has_models = Confirm.ask(
        "\n¿Vas a agregar modelos ahora?",
        default=True
    )

    models_dict = {}
    if has_models:
        console.print("\n[bold]Agregar Modelos:[/bold]")
        while True:
            model_name = Prompt.ask("📦 [bold]Nombre del modelo[/bold]", default="")

            if not model_name:
                break

            models_dict[model_name] = {"name": model_name}

            add_more = Confirm.ask("\n¿Agregar otro modelo?", default=False)
            if not add_more:
                break

    # Crear y guardar provider
    provider_config = ProviderConfig(
        type="ollama",
        options={"base_url": base_url, "apiKey": api_key},
        models=models_dict
    )

    config.add_provider(name, provider_config)

    console.print(f"\n[bold green]✓ Provider '{name}' agregado exitosamente![/bold green]")
    console.print(f"📍 URL: {base_url}")
    if models_dict:
        console.print(f"📦 Modelos: {', '.join(models_dict.keys())}")
