"""Global constants for Partner OS."""

from __future__ import annotations

from pathlib import Path

SYSTEM_NAME = "Partner OS"
MANAGER_NAME = "The Manager"
FIRM_INBOX_FILENAME = "00_FIRM_INBOX.md"
FIRM_LIBRARY_DIRNAME = "00_FIRM_LIBRARY"
STAGING_DIRNAME = "_STAGING_INBOX"
DATABASE_FILENAME = "firm_intelligence.db"

DEAL_JACKET_SUBDIRS = (
    "01_Intel_Photos",
    "02_Intel_Video",
    "03_Intel_Audio",
    "04_Intel_Docs",
    "05_System_State",
    "06_AI_Deliverables",
)

EXTENSION_TO_SUBDIR = {
    ".jpg": "01_Intel_Photos",
    ".jpeg": "01_Intel_Photos",
    ".png": "01_Intel_Photos",
    ".mp4": "02_Intel_Video",
    ".mov": "02_Intel_Video",
    ".mp3": "03_Intel_Audio",
    ".wav": "03_Intel_Audio",
    ".pdf": "04_Intel_Docs",
    ".doc": "04_Intel_Docs",
    ".docx": "04_Intel_Docs",
    ".txt": "04_Intel_Docs",
    ".md": "04_Intel_Docs",
}

HIGH_CONFIDENCE_DOMAINS = {
    "vancouverwa.gov",
    "clark.wa.gov",
    "sec.gov",
    "wsj.com",
    "bloomberg.com",
    "fred.stlouisfed.org",
    "treasury.gov",
    "federalreserve.gov",
    "bls.gov",
    "bea.gov",
}

MEDIUM_CONFIDENCE_DOMAINS = {
    "costar.com",
    "bizjournals.com",
    "oregonlive.com",
    "columbian.com",
    "pdxpipeline.com",
}

DEFAULT_FIRM_INBOX_HEADER = "# 00_FIRM_INBOX\n\nThis file is the human review queue for Daniil and Roman.\n\n"

WA_TOKENS = {"wa", "washington"}


def is_within_directory(base_dir: Path, target: Path) -> bool:
    """Return True when target is within base_dir."""
    base = base_dir.resolve()
    child = target.resolve()
    return str(child).startswith(str(base))
