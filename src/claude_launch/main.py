"""Entry point para el CLI de Claude Launch."""

import os
import sys
import subprocess
import argparse

# Forzar UTF-8 en Windows para emojis y caracteres especiales
if sys.platform == "win32":
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

from rich.panel import Panel

from claude_launch.console import console
from claude_launch.config import ConfigWrapper
from claude_launch.cli import run_provider_selection, run_new_provider


def _get_version_info():
    """Obtener versión y hash del commit."""
    ver = "unknown"

    # 1. Intentar obtener __version__ del paquete (funciona siempre)
    try:
        from claude_launch import __version__
        ver = __version__
    except Exception:
        # 2. Intentar obtener versión de importlib.metadata (funciona con metadata incluido)
        try:
            from importlib.metadata import version
            ver = version("claude-launch")
        except Exception:
            ver = "unknown"

    # 3. Intentar obtener hash del archivo _commit.py (incrustado durante build de PyInstaller)
    try:
        from claude_launch._commit import COMMIT_HASH
        if COMMIT_HASH:
            return ver, COMMIT_HASH
    except Exception:
        pass

    # 4. Intentar obtener hash de variable de entorno (para builds de CI/CD)
    hash_commit = os.environ.get("CCL_COMMIT_HASH", "")
    if hash_commit:
        return ver, hash_commit

    # 5. Intentar obtener hash desde git (para desarrollo local)
    try:
        hash_commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        if not hash_commit:
            hash_commit = "unknown"
    except Exception:
        hash_commit = "unknown"

    return ver, hash_commit


def _split_args(argv: list[str]) -> tuple[list[str], list[str]]:
    """Separar argumentos del CLI y argumentos para Claude Code.

    Todo lo que viene después de '--' se pasa directamente a Claude Code.

    Args:
        argv: sys.argv[1:]

    Returns:
        Tupla (args_cli, args_claude)
    """
    if "--" in argv:
        sep = argv.index("--")
        return argv[:sep], argv[sep + 1:]
    return argv, []


def main():
    """Entrada principal del programa.

    Uso:
        ccl                             - Muestra menú principal
        ccl <provider>                  - Listar y seleccionar modelos de un provider
        ccl <provider> --model <name>   - Lanzar Claude con modelo específico
        ccl <provider> --model <name> -- --flag  - Pasar flags a Claude Code
        ccl --new                       - Agregar nuevo provider
        ccl --list                      - Listar todos los providers configurados
        ccl -r <provider>               - Eliminar un provider existente
        ccl --help                      - Mostrar ayuda

    Ejemplos:
        ccl mole --model qwen3.5:35b
        ccl mole --model qwen3.5:35b -- --dangerously-skip-permissions
        ccl chati --model mistral:latest -- --verbose --timeout=60
        ccl -r pp                       # Eliminar provider 'pp'
    """
    version, commit_hash = _get_version_info()

    # Separar args del CLI y args para Claude Code (después de --)
    cli_argv, extra_args = _split_args(sys.argv[1:])

    parser = argparse.ArgumentParser(
        prog="ccl",
        description=f"Claude Launch v{version} ({commit_hash}) - Lanza Claude Code con múltiples providers Ollama"
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
        "--remove", "-r",
        dest="remove_provider",
        metavar="PROVIDER",
        help="Eliminar un provider existente"
    )

    args = parser.parse_args(cli_argv)

    # Cargar configuración
    config_path = args.config
    try:
        config = ConfigWrapper(config_path)
    except FileNotFoundError:
        console.print(Panel(
            f"[red]ERROR: No se encontró el archivo de configuración en: {config_path}[/red]\n\n"
            "Ejecuta [bold]ccl --new[/bold] para crear uno nuevo.",
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
                "Ejecuta [bold]ccl --new[/bold] para agregar uno.",
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
        try:
            run_new_provider()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
            sys.exit(0)
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
            # Lanzar directamente con el modelo especificado
            from claude_launch.launcher import ClaudeLauncher
            launcher = ClaudeLauncher(
                provider.options.base_url,
                provider.options.api_key,
                model=args.model,
                extra_args=extra_args,
            )
            try:
                exit_code = launcher.launch_interactive()
                sys.exit(exit_code)
            except RuntimeError as e:
                console.print(Panel(
                    f"[red]ERROR:[/red] [bold]{e}[/bold]",
                    title="Claude Code no instalado",
                    border_style="red"
                ))
                sys.exit(1)
        else:
            # Modo interactivo - mostrar lista y seleccionar
            try:
                run_provider_selection(provider, extra_args=extra_args)
            except KeyboardInterrupt:
                console.print("\n[yellow]Operación cancelada por el usuario.[/yellow]")
                sys.exit(0)

    else:
        # Sin argumentos - mostrar help
        parser.print_help()


if __name__ == "__main__":
    main()
