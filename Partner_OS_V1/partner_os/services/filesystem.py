"""Filesystem contracts and helpers."""

from __future__ import annotations

from pathlib import Path

from partner_os.config import AppConfig
from partner_os.constants import DEAL_JACKET_SUBDIRS, DEFAULT_FIRM_INBOX_HEADER



def ensure_runtime_layout(config: AppConfig) -> None:
    """Create required top-level directories/files."""
    config.root_dir.mkdir(parents=True, exist_ok=True)
    config.staging_inbox_dir.mkdir(parents=True, exist_ok=True)
    config.firm_library_dir.mkdir(parents=True, exist_ok=True)
    if not config.firm_inbox_path.exists():
        config.firm_inbox_path.write_text(DEFAULT_FIRM_INBOX_HEADER, encoding="utf-8")



def deal_root(config: AppConfig, deal_id: str, slug: str) -> Path:
    return config.root_dir / f"{deal_id}_{slug}"



def ensure_deal_jacket(config: AppConfig, deal_id: str, slug: str) -> Path:
    root = deal_root(config, deal_id, slug)
    root.mkdir(parents=True, exist_ok=True)
    for subdir in DEAL_JACKET_SUBDIRS:
        (root / subdir).mkdir(parents=True, exist_ok=True)
    return root



def append_firm_inbox(config: AppConfig, content: str) -> None:
    with config.firm_inbox_path.open("a", encoding="utf-8") as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")



def newest_markdown_files(directory: Path, limit: int = 3) -> list[Path]:
    files = sorted(directory.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]
