"""Base agent type."""

from __future__ import annotations

from dataclasses import dataclass

from partner_os.config import AppConfig
from partner_os.db.store import DataStore


@dataclass(slots=True)
class BaseAgent:
    name: str
    config: AppConfig
    store: DataStore
