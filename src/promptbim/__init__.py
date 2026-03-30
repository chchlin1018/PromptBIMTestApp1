"""PromptBIMTestApp1 — AI-Powered BIM Building Generator

Lazy-loaded package: heavy submodules (agents, bim, viz, mcp, voice) are
imported on first access to keep startup time under 1s.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("promptbim")
except PackageNotFoundError:
    __version__ = "2.12.0"
except ImportError:
    __version__ = "2.12.0"

__author__ = "Michael Lin (Reality Matrix Inc.)"

__all__ = [
    "__version__",
    "__author__",
]

# Lazy submodule loading to reduce startup time and memory usage.
_LAZY_SUBMODULES = {
    "agents",
    "bim",
    "codes",
    "gui",
    "land",
    "mcp",
    "schemas",
    "viz",
    "voice",
    "web",
}

if TYPE_CHECKING:
    pass


def __getattr__(name: str):
    if name in _LAZY_SUBMODULES:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
