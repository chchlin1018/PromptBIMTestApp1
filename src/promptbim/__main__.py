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

    # check subcommand
    check_parser = subparsers.add_parser("check", help="Run system health checks")
    check_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    check_parser.add_argument(
        "--ai", action="store_true", help="Only run AI-related checks"
    )
    check_parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix failed checks"
    )
    check_parser.add_argument(
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
    elif args.command == "check":
        _run_check(args)
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


def _run_check(args):
    import json
    from promptbim.startup.health_check import HealthChecker

    checker = HealthChecker()

    if args.ai:
        results = checker.run_ai_only()
    else:
        results = checker.run_all()

    if args.json:
        output = {
            "results": checker.to_dict(),
            "summary": checker.summary(),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        _print_check_results(results, checker.summary())

    if args.fix:
        from promptbim.startup.auto_fix import auto_fix_all
        failed = [r for r in results if r.status == "fail"]
        if failed:
            print("\nAttempting auto-fix...")
            fix_results = auto_fix_all(failed)
            for fr in fix_results:
                status = "\u2705" if fr.success else "\u274c"
                print(f"  {status} {fr.check_name}: {fr.output[:80]}")
        else:
            print("\nNo failed checks to fix.")

    summary = checker.summary()
    sys.exit(0 if summary["all_passed"] else 1)


def _print_check_results(results, summary):
    icons = {"pass": "\u2705", "fail": "\u274c", "warn": "\u26a0\ufe0f", "skip": "\u23ed\ufe0f"}
    current_category = ""

    print("\n  PromptBIM \u2014 System Health Check")
    print("  " + "\u2500" * 40)

    for r in results:
        if r.category != current_category:
            current_category = r.category
            print(f"\n  {current_category}")

        icon = icons.get(r.status, "?")
        elapsed = f" ({r.elapsed_ms:.0f}ms)" if r.elapsed_ms > 0 else ""
        print(f"  {icon} {r.name}: {r.message}{elapsed}")

        if r.status in ("fail", "warn"):
            if r.detail:
                print(f"     \u2192 Error: {r.detail}")
            if r.fix_hint:
                print(f"     \u2192 Fix: {r.fix_hint}")

    print(f"\n  \u2500\u2500 {summary['passed']}/{summary['total']} passed", end="")
    if summary["warned"]:
        print(f", {summary['warned']} warnings", end="")
    if summary["failed"]:
        print(f", {summary['failed']} failed", end="")
    print(" \u2500\u2500\n")


if __name__ == "__main__":
    app()
