"""Application configuration using Pydantic BaseSettings."""

import os
from pathlib import Path

from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

from promptbim.debug import get_logger

logger = get_logger("config")


def _find_env_file() -> str | None:
    """Search for .env file in multiple locations.

    Search order:
    1. Current working directory
    2. Source package root (src/promptbim/../../.env)
    3. Well-known project path (~/Documents/MyProjects/PromptBIMTestApp1/.env)
    4. Environment variable PROMPTBIM_ENV_FILE
    """
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent / ".env",
        Path.home() / "Documents" / "MyProjects" / "PromptBIMTestApp1" / ".env",
        Path.home() / "documents" / "myprojects" / "PromptBIMTestApp1" / ".env",
    ]

    # Also check env var for explicit path
    env_file_override = os.getenv("PROMPTBIM_ENV_FILE")
    if env_file_override:
        env_paths.insert(0, Path(env_file_override))

    for p in env_paths:
        if p.exists():
            logger.debug("Found .env at: %s", p)
            return str(p)

    logger.debug("No .env file found in any searched path")
    return None


def validate_api_key(key: str) -> bool:
    """Validate Anthropic API key format.

    Valid formats: sk-ant-api03-... or sk-ant-...
    Returns True if key is empty (not set) or matches expected format.
    """
    if not key:
        return True
    return key.startswith("sk-ant-") and len(key) >= 20


class Settings(BaseSettings):
    """PromptBIM application settings, loaded from .env file."""

    # API
    anthropic_api_key: str = Field(default="", description="Anthropic Claude API key")
    claude_model: str = Field(default="claude-sonnet-4-20250514", description="Claude model to use")

    # Paths
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    # Defaults
    default_city: str = Field(default="Taipei", description="Default city for zoning lookup")
    log_level: str = Field(default="INFO", description="Log level")

    # API
    api_timeout_seconds: float = Field(default=30.0, description="Anthropic API call timeout in seconds")

    # Debug
    debug_mode: bool = Field(default=False, description="Enable debug logging")

    # Startup check
    startup_check_enabled: bool = Field(default=True, description="Run health check on startup")
    startup_check_skip_ai: bool = Field(default=False, description="Skip AI checks (offline mode)")
    ai_ping_timeout_seconds: float = Field(default=10.0, description="AI ping timeout in seconds")
    ai_model: str = Field(default="claude-sonnet-4-20250514", description="Default AI model")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    env_file = _find_env_file()
    if env_file:
        # Check .env file permissions (warn if world-readable)
        env_path = Path(env_file)
        try:
            mode = env_path.stat().st_mode
            if mode & 0o044:  # group or other readable
                logger.warning(
                    ".env file %s is readable by group/others. "
                    "Run: chmod 600 %s",
                    env_file,
                    env_file,
                )
        except OSError:
            pass
        settings = Settings(_env_file=env_file)
    else:
        settings = Settings(_env_file=None)

    # Validate API key format
    if settings.anthropic_api_key and not validate_api_key(settings.anthropic_api_key):
        logger.warning(
            "API key does not match expected Anthropic format (sk-ant-...). "
            "Please check your ANTHROPIC_API_KEY in .env"
        )

    return settings
