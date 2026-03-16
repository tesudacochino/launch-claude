"""Entry point para el CLI de Claude Launch."""

import sys
import argparse

# Forzar UTF-8 en Windows para emojis y caracteres especiales
if sys.platform == "win32":
    import os
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Configurar encoding de stdout/stderr
    if sys.stdout is not None and not sys.stdout.encoding == "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if sys.stderr is not None:
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

from rich.console import Console
from rich.panel import Panel

from claude_launch.config import ConfigWrapper, ProviderConfig
from claude_launch.cli import run_provider_selection, run_new_provider


console = Console()


def main():
    """Entrada principal del programa.

    Uso:
        cl                              - Muestra menú principal
        cl <provider>                   - Listar y seleccionar modelos de un provider
        cl <provider> --model <name>    - Lanzar Claude con modelo específico
        cl <provider> --model <name> -- --flag  - Pasar flags a Claude Code
        cl --new                        - Agregar nuevo provider
        cl --list                       - Listar todos los providers configurados
        cl -r <provider>                - Eliminar un provider existente
        cl --help                       - Mostrar ayuda

    Ejemplos:
        cl mole --model qwen3.5:35b
        cl mole --model qwen3.5:35b -- --dangerously-skip-permissions
        cl chati --model mistral:latest -- --verbose --timeout=60
        cl -r pp                        # Eliminar provider 'pp'
    """
    parser = argparse.ArgumentParser(
        prog="cl",
        description="Claude Launch - Lanza Claude Code con múltiples providers Ollama"
    )

    parser.add_argument(
        "provider",
        nargs="?",
        help="Nombre del provider a usar"
    )

    parser.add_argument(
        "--model", "-m",
        help="Nombre específico del modelo a usar"
    )

    parser.add_argument(
        "--new", "-n",
        action="store_true",
        help="Abrir asistente para agregar nuevo provider"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Listar todos los providers configurados"
    )

    parser.add_argument(
        "--config", "-c",
        help="Ruta al archivo de configuración"
    )

    parser.add_argument(
        "--dangerously-skip-permissions", "-d",
        action="store_true",
        help="Skip permission checks when launching Claude Code (passes --dangerously-skip-permissions to claude)"
    )

    parser.add_argument(
        "--remove", "-r",
        dest="remove_provider",
        metavar="PROVIDER",
        help="Eliminar un provider existente"
    )

    # Usar parse_known_args para capturar argumentos adicionales después de --
    args, extra_args = parser.parse_known_args()

    # Filtrar flags propios del CLI y pasar el resto a Claude
    if extra_args:
        cli_options_with_values = {"--model", "-m", "--config", "-c"}
        extra_args_filtered = []
        skip_next = False

        for i, arg in enumerate(extra_args):
            if skip_next:
                skip_next = False
                continue

            # Skip flags propios del CLI (incluyendo -d que ya fue capturado)
            if arg in cli_options_with_values:
                skip_next = True
                continue
            if arg in {"--new", "-n", "--list", "-l"}:
                continue
            if arg in {"--dangerously-skip-permissions", "-d"}:
                continue

            extra_args_filtered.append(arg)

        args.extra_args = extra_args_filtered
    else:
        args.extra_args = []

    # Si se pasó -d explícitamente, agregarlo a extra_args (si no está ya)
    if hasattr(args, 'dangerously_skip_permissions') and args.dangerously_skip_permissions:
        if "--dangerously-skip-permissions" not in args.extra_args:
            args.extra_args.append("--dangerously-skip-permissions")

    # Pasar los flags de configuración al atributo correspondiente
    args.config = getattr(args, 'config', None)

    # Cargar configuración
    config_path = args.config or "config.json"
    try:
        config = ConfigWrapper(config_path)
    except FileNotFoundError:
        console.print(Panel(
            f"[red]ERROR: No se encontró el archivo de configuración en: {config_path}[/red]\n\n"
            "Ejecuta [bold]cl --new[/bold] para crear uno nuevo.",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

    # Casos de uso
    if args.remove_provider:
        # Modo eliminar provider
        provider_name = args.remove_provider
        if provider_name not in config.providers:
            console.print(Panel(
                f"[red]ERROR: Provider '{provider_name}' no encontrado.[/red]\n\n"
                "Providers disponibles:\n" +
                "\n".join(f"  - {p}" for p in config.providers.keys()),
                title="Error",
                border_style="red"
            ))
            sys.exit(1)

        from rich.prompt import Confirm
        if not Confirm.ask(f"¿Estás seguro de que quieres eliminar el provider [bold]{provider_name}[/bold]?", default=False):
            console.print("[yellow]Operación cancelada.[/yellow]")
            return

        if config.remove_provider(provider_name):
            console.print(Panel(
                f"[green]✓ Provider '{provider_name}' eliminado correctamente.[/green]",
                title="Éxito",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]ERROR: No se pudo eliminar el provider '{provider_name}'.[/red]",
                title="Error",
                border_style="red"
            ))
            sys.exit(1)
        return

    if args.list:
        # Listar providers configurados
        if not config.providers:
            console.print(Panel(
                "[yellow]No hay providers configurados.[/yellow]\n\n"
                "Ejecuta [bold]cl --new[/bold] para agregar uno.",
                title="Providers",
                border_style="yellow"
            ))
        else:
            lines = [f"  [green]•[/green] {name} [dim]({provider.options.base_url})[/dim]"
                     for name, provider in sorted(config.providers.items())]
            console.print(Panel(
                f"[bold]Providers configurados:[/bold]\n\n" + "\n".join(lines),
                title="Providers",
                border_style="green"
            ))
        return

    if args.new:
        # Modo agregar nuevo provider
        run_new_provider()
        return

    if args.provider:
        # Verificar que el provider existe
        if args.provider not in config.providers:
            console.print(Panel(
                f"[red]ERROR: Provider '{args.provider}' no encontrado.[/red]\n\n"
                "Providers disponibles:\n" +
                "\n".join(f"  - {p}" for p in config.providers.keys()),
                title="Error",
                border_style="red"
            ))
            sys.exit(1)

        provider = config.providers[args.provider]

        if args.model:
            # Verificar que el modelo existe antes de lanzar
            from claude_launch.ollama_api import OllamaAPI
            ollama_api = OllamaAPI(
                provider.options.base_url,
                provider.options.api_key
            )

            # Obtener modelos disponibles de la API
            try:
                available_models = ollama_api.list_models()
            except ConnectionError:
                console.print("[red]ERROR: No se pudieron verificar los modelos.[/red]")
                console.print("Usa el modo interactivo sin --model para seleccionar.")
                sys.exit(1)

            if args.model not in available_models:
                console.print(f"\n[red]ERROR: El modelo '{args.model}' no está disponible.[/red]")
                console.print("Modelos disponibles:")
                for m in available_models:
                    console.print(f"  - {m}")
                sys.exit(1)

            # Lanzar Claude directamente con el modelo especificado
            from claude_launch.launcher import ClaudeLauncher
            launcher = ClaudeLauncher(
                provider.options.base_url,
                provider.options.api_key,
                model=args.model,
                dangerously_skip_permissions=False,  # Ya está en extra_args si se pasó -d
                extra_args=args.extra_args
            )
            exit_code = launcher.launch_interactive()
            sys.exit(exit_code)
        else:
            # Modo interactivo - mostrar lista y seleccionar
            from claude_launch.cli import run_provider_selection
            run_provider_selection(provider, extra_args=args.extra_args)

    else:
        # Sin argumentos - mostrar help
        parser.print_help()


if __name__ == "__main__":
    main()
