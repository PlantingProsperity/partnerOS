"""ID and slug helpers."""

from __future__ import annotations

import re
import uuid
from datetime import datetime


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return cleaned.strip("-") or "unknown"



def new_deal_id() -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"deal-{stamp}-{uuid.uuid4().hex[:6]}"



def new_task_id() -> str:
    return f"task-{uuid.uuid4().hex}"
