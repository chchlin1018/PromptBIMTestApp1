"""Unified Debug Logging System for PromptBIM.

Usage in any module:
    from promptbim.debug import get_logger
    logger = get_logger("land.geojson")
    logger.debug("Loading file: %s", path)

Debug mode activation (any of these):
    1. Environment variable: PROMPTBIM_DEBUG=1
    2. CLI argument: python -m promptbim gui --debug
    3. .env file: PROMPTBIM_DEBUG=1
    4. Runtime: from promptbim.debug import enable_debug; enable_debug()
"""

import logging
import os
import sys
from pathlib import Path

DEBUG_MODE = os.getenv("PROMPTBIM_DEBUG", "0") == "1"

# ANSI color codes for module-based coloring
_COLORS = {
    "land": "\033[32m",       # green
    "bim": "\033[34m",        # blue
    "agents": "\033[35m",     # magenta
    "codes": "\033[33m",      # yellow
    "gui": "\033[36m",        # cyan
    "viz": "\033[36m",        # cyan
    "mep": "\033[34;1m",      # bright blue
    "cost": "\033[33;1m",     # bright yellow
    "monitoring": "\033[31m", # red
    "simulation": "\033[31;1m",  # bright red
    "voice": "\033[35;1m",    # bright magenta
    "mcp": "\033[32;1m",      # bright green
    "web": "\033[32;1m",      # bright green
}
_RESET = "\033[0m"


class _ColorFormatter(logging.Formatter):
    """Formatter that colorizes the logger name based on module category."""

    def __init__(self, use_color: bool = True):
        super().__init__(
            fmt="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        self._use_color = use_color and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self._use_color:
            name = record.name
            # Extract category from "promptbim.{category}...."
            parts = name.split(".")
            category = parts[1] if len(parts) > 1 else ""
            color = _COLORS.get(category, "")
            if color:
                record.name = f"{color}{name}{_RESET}"
        return super().format(record)


def get_logger(module_name: str) -> logging.Logger:
    """Get a module-specific logger with unified formatting.

    Args:
        module_name: Dotted module path, e.g. "land.geojson" or "bim.ifc".
                     Will be prefixed with "promptbim." automatically.
    """
    full_name = f"promptbim.{module_name}"
    logger = logging.getLogger(full_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(_ColorFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)
    return logger


def enable_debug():
    """Enable debug mode at runtime — sets all promptbim loggers to DEBUG."""
    global DEBUG_MODE
    DEBUG_MODE = True
    for name in list(logging.Logger.manager.loggerDict):
        if name.startswith("promptbim."):
            logging.getLogger(name).setLevel(logging.DEBUG)


def disable_debug():
    """Disable debug mode at runtime — sets all promptbim loggers to WARNING."""
    global DEBUG_MODE
    DEBUG_MODE = False
    for name in list(logging.Logger.manager.loggerDict):
        if name.startswith("promptbim."):
            logging.getLogger(name).setLevel(logging.WARNING)


def setup_file_logging(log_dir: str | Path = "logs"):
    """Optionally enable file-based logging to logs/ directory."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    filename = log_path / f"promptbim_{datetime.now():%Y%m%d_%H%M%S}.log"

    file_handler = logging.FileHandler(filename, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    file_handler.setLevel(logging.DEBUG)

    root = logging.getLogger("promptbim")
    root.addHandler(file_handler)
    root.setLevel(logging.DEBUG)

    return filename
