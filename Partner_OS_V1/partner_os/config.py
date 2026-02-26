"""Application configuration loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from partner_os.constants import (
    DATABASE_FILENAME,
    FIRM_INBOX_FILENAME,
    FIRM_LIBRARY_DIRNAME,
    STAGING_DIRNAME,
)


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    database_path: Path
    staging_inbox_dir: Path
    firm_library_dir: Path
    firm_inbox_path: Path
    gemini_api_key: str
    gemini_model: str
    gemini_timeout_seconds: int



def load_config(root_override: Path | None = None) -> AppConfig:
    """Load environment-driven runtime configuration."""
    load_dotenv()

    if root_override:
        root_dir = root_override.resolve()
    else:
        env_root = os.getenv("PARTNER_OS_ROOT")
        if env_root:
            root_dir = Path(env_root).expanduser().resolve()
        else:
            root_dir = Path(__file__).resolve().parents[1]

    database_path = root_dir / DATABASE_FILENAME
    staging_inbox_dir = root_dir / STAGING_DIRNAME
    firm_library_dir = root_dir / FIRM_LIBRARY_DIRNAME
    firm_inbox_path = root_dir / FIRM_INBOX_FILENAME

    return AppConfig(
        root_dir=root_dir,
        database_path=database_path,
        staging_inbox_dir=staging_inbox_dir,
        firm_library_dir=firm_library_dir,
        firm_inbox_path=firm_inbox_path,
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip(),
        gemini_timeout_seconds=int(os.getenv("GEMINI_TIMEOUT_SECONDS", "20")),
    )
