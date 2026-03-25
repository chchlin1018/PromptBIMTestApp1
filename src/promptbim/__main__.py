"""PromptBIMTestApp1 CLI entry point."""

import argparse
import sys

from promptbim import __version__


def app():
    parser = argparse.ArgumentParser(
        prog="promptbim",
        description="PromptBIM - AI-Powered BIM Building Generator",
    )
    parser.add_argument(
        "--version", action="version", version=f"promptbim {__version__}"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging output"
    )

    subparsers = parser.add_subparsers(dest="command")

    # gui subcommand
    gui_parser = subparsers.add_parser("gui", help="Launch the desktop GUI")
    gui_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging output"
    )

    # generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate building from prompt")
    gen_parser.add_argument("prompt", help="Building description prompt")
    gen_parser.add_argument("--land", help="Path to land data file (GeoJSON/SHP/DXF)")
    gen_parser.add_argument("--output", "-o", default="./output", help="Output directory")
    gen_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging output"
    )

    args = parser.parse_args()

    if args.debug:
        from promptbim.debug import enable_debug
        enable_debug()

    if args.command == "gui":
        _launch_gui()
    elif args.command == "generate":
        print(f"[promptbim] Generate not yet implemented. Prompt: {args.prompt}")
    else:
        parser.print_help()


def _launch_gui():
    try:
        from promptbim.gui.main_window import launch_main_window

        launch_main_window()
    except ImportError as e:
        print(f"[promptbim] GUI dependencies not available: {e}", file=sys.stderr)
        print("[promptbim] Install PySide6: pip install PySide6", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    app()
