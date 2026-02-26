"""Shared typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class TaskType(str, Enum):
    create_deal_jacket = "create_deal_jacket"
    triage_file = "triage_file"
    run_cfo = "run_cfo"
    run_scout = "run_scout"
    append_firm_inbox = "append_firm_inbox"


@dataclass(slots=True)
class Task:
    task_id: str
    task_type: TaskType
    deal_id: str
    actor: str
    payload: dict[str, Any]
    rationale: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class AgentResult:
    summary: str
    rationale: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CFOInput:
    purchase_price: float
    current_noi: float
    pro_forma_noi: float
    annual_debt_service: float
    annual_cash_flow: float
    total_cash_invested: float
    arv: float
    rehab_budget: float
    market_cap_rate: float
    cash_flows: list[float]


@dataclass(slots=True)
class ScoutClaim:
    title: str
    url: str
    summary: str
    timestamp_utc: str
    confidence_label: str
    confidence_score: int


@dataclass(slots=True)
class StagedFile:
    staged_path: Path
    original_name: str
