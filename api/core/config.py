"""
Application configuration.
Reads settings from environment variables.
"""
import os
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables."""

    # Gemini API
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3-pro")

    # File storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR: Path = BASE_DIR / "tmp"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # Session
    SESSION_TTL_SECONDS: int = int(os.environ.get("SESSION_TTL", "3600"))  # 1 hour

    # Document processing
    MAX_WORD_COUNT_WITHOUT_SUMMARIZATION: int = 5000

    def __init__(self):
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
