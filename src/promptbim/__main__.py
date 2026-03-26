"""PromptBIMTestApp1 CLI entry point."""

import argparse
import sys

from promptbim import __version__


def app():
    parser = argparse.ArgumentParser(
        prog="promptbim",
        description="PromptBIM - AI-Powered BIM Building Generator",
        epilog=(
            "Security: Store your API key in .env (chmod 600 .env). "
            "Never commit .env to git. Key format: sk-ant-api03-..."
        ),
    )
    parser.add_argument("--version", action="version", version=f"promptbim {__version__}")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    subparsers = parser.add_subparsers(dest="command")

    # gui subcommand
    gui_parser = subparsers.add_parser("gui", help="Launch the desktop GUI")
    gui_parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    # generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate building from prompt")
    gen_parser.add_argument("prompt", help="Building description prompt")
    gen_parser.add_argument("--land", help="Path to land data file (GeoJSON/SHP/DXF/KML)")
    gen_parser.add_argument("--output", "-o", default="./output", help="Output directory")
    gen_parser.add_argument(
        "--format",
        choices=["ifc", "usd", "both"],
        default="both",
        help="Output format (default: both)",
    )
    gen_parser.add_argument(
        "--city", default="Taipei", help="City for zoning rules lookup (default: Taipei)"
    )
    gen_parser.add_argument(
        "--template",
        choices=["residential", "school", "hospital", "factory"],
        help="Use a building template instead of AI planning",
    )
    gen_parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    # check subcommand
    check_parser = subparsers.add_parser("check", help="Run system health checks")
    check_parser.add_argument("--json", action="store_true", help="Output results as JSON")
    check_parser.add_argument("--ai", action="store_true", help="Only run AI-related checks")
    check_parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix failed checks"
    )
    check_parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    args = parser.parse_args()

    if args.debug:
        from promptbim.debug import enable_debug

        enable_debug()

    if args.command == "gui":
        _launch_gui()
    elif args.command == "generate":
        _run_generate(args)
    elif args.command == "check":
        _run_check(args)
    else:
        parser.print_help()


def _run_generate(args):
    """Run the generate pipeline from CLI."""
    import json
    from pathlib import Path

    from promptbim.agents.orchestrator import Orchestrator
    from promptbim.config import get_settings
    from promptbim.debug import get_logger
    from promptbim.schemas.zoning import ZoningRules

    logger = get_logger("cli.generate")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load land data
    land = None
    if args.land:
        land = _load_land_file(args.land)
    else:
        from promptbim.schemas.land import LandParcel

        land = LandParcel(
            name="CLI-Default",
            boundary=[(0, 0), (30, 0), (30, 30), (0, 30)],
            area_sqm=900.0,
        )

    # Zoning rules with city
    settings = get_settings()
    city = getattr(args, "city", None) or settings.default_city
    zoning = ZoningRules(city=city)

    # Generate
    orch = Orchestrator(output_dir=output_dir, on_status=_cli_status)
    result = orch.generate(args.prompt, land, zoning)

    if result.success:
        print(f"Generated: {result.building_name}")
        if result.ifc_path:
            print(f"   IFC: {result.ifc_path}")
        if result.usd_path:
            print(f"   USD: {result.usd_path}")
        print(f"   Stories: {result.summary.get('stories', '?')}")
        # Save JSON summary
        summary_path = output_dir / "result.json"
        summary_path.write_text(
            json.dumps(
                result.model_dump(mode="json", exclude={"ifc_path", "usd_path"}),
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )
        print(f"   Summary: {summary_path}")
    else:
        print(f"Generation failed: {result.errors}", file=sys.stderr)
        sys.exit(1)


def _load_land_file(path_str: str):
    """Auto-detect land file format and parse."""
    from pathlib import Path

    from promptbim.debug import get_logger

    logger = get_logger("cli.generate")
    path = Path(path_str)

    if not path.exists():
        print(f"Land file not found: {path}", file=sys.stderr)
        sys.exit(1)

    ext = path.suffix.lower()

    if ext in (".geojson", ".json"):
        from promptbim.land.parsers.geojson import parse_geojson

        parcels = parse_geojson(path)
    elif ext == ".shp":
        from promptbim.land.parsers.shapefile import parse_shapefile

        parcels = parse_shapefile(path)
    elif ext == ".dxf":
        from promptbim.land.parsers.dxf import parse_dxf

        parcels = parse_dxf(path)
    elif ext in (".kml", ".kmz"):
        from promptbim.land.parsers.kml import parse_kml

        parcels = parse_kml(path)
    else:
        print(f"Unsupported land file format: {ext}", file=sys.stderr)
        sys.exit(1)

    if not parcels:
        print(f"No land parcels found in: {path}", file=sys.stderr)
        sys.exit(1)

    logger.info("Loaded %d parcel(s) from %s", len(parcels), path.name)
    return parcels[0]


def _cli_status(status):
    """Print pipeline progress to console."""
    print(f"  [{status.stage}] {status.message} ({status.progress:.0%})")


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
