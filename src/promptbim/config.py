"""Application configuration using Pydantic BaseSettings."""

from pathlib import Path

from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    """PromptBIM application settings, loaded from .env file."""

    # API
    anthropic_api_key: str = Field(default="", description="Anthropic Claude API key")
    claude_model: str = Field(
        default="claude-sonnet-4-20250514", description="Claude model to use"
    )

    # Paths
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    f3d_path: str = Field(default="f3d", description="F3D binary path")

    # Defaults
    default_city: str = Field(default="Taipei", description="Default city for zoning lookup")
    log_level: str = Field(default="INFO", description="Log level")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()
