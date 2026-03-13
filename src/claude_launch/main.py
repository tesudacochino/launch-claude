"""Entry point para el CLI de Claude Launch."""

import sys
import argparse
from rich.console import Console

from .config import ConfigWrapper, ProviderConfig
from .cli import run_provider_selection, run_new_provider


console = Console()


def main():
    """Entrada principal del programa.

    Uso:
        cl                    - Muestra menú principal
        cl <provider>         - Listar y seleccionar modelos de un provider
        cl --new              - Agregar nuevo provider
        cl <provider> --model <name>  - Lanzar Claude con modelo específico
        cl --help             - Mostrar ayuda
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
        "--config", "-c",
        help="Ruta al archivo de configuración"
    )

    args = parser.parse_args()

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
            from .ollama_api import OllamaAPI
            ollama_api = OllamaAPI(
                provider.options.base_url,
                provider.options.api_key
            )

            # Obtener modelos disponibles de la API
            try:
                available_models = ollama_api.list_models()
            except ConnectionError:
                available_models = list(provider.models.keys())

            if args.model not in available_models:
                console.print(f"\n[red]ERROR: El modelo '{args.model}' no está disponible.[/red]")
                console.print("Modelos disponibles:")
                for m in available_models:
                    console.print(f"  - {m}")
                sys.exit(1)

            # Lanzar Claude directamente con el modelo especificado
            from .launcher import ClaudeLauncher
            launcher = ClaudeLauncher(
                provider.options.base_url,
                provider.options.api_key,
                model=args.model
            )
            exit_code = launcher.launch_interactive()
            sys.exit(exit_code)
        else:
            # Modo interactivo - mostrar lista y seleccionar
            run_provider_selection(provider)

    else:
        # Sin argumentos - mostrar menú principal (placeholder para futuro)
        console.print("\n[bold blue]Claude Launch[/bold blue]\n")
        console.print("Usa este CLI para lanzar Claude Code con diferentes providers:\n")
        console.print("  [bold]cl <provider>[/bold]     - Seleccionar modelo y lanzar")
        console.print("  [bold]cl <provider> --model <name>[/bold]  - Lanzar directamente con un modelo específico")
        console.print("  [bold]cl --new[/bold]              - Agregar nuevo provider\n")

        # Opcional: mostrar menú interactivo en el futuro
        # run_menu()


if __name__ == "__main__":
    main()
