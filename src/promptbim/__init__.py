"""PromptBIMTestApp1 — AI-Powered BIM Building Generator"""

try:
    from importlib.metadata import version

    __version__ = version("promptbim")
except Exception:
    __version__ = "2.6.0"

__author__ = "Michael Lin (Reality Matrix Inc.)"

__all__ = [
    "__version__",
    "__author__",
]
