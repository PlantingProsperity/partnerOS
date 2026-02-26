from __future__ import annotations

from pathlib import Path

import pytest

from partner_os.runtime import AppRuntime, build_runtime


@pytest.fixture
def runtime_no_llm(tmp_path: Path) -> AppRuntime:
    runtime = build_runtime(root_override=tmp_path, use_llm=False)
    yield runtime
    runtime.close()


@pytest.fixture
def runtime_with_gemini(tmp_path: Path) -> AppRuntime:
    runtime = build_runtime(root_override=tmp_path, use_llm=True)
    yield runtime
    runtime.close()


@pytest.fixture
def default_cfo_payload() -> dict[str, object]:
    return {
        "purchase_price": 250000.0,
        "current_noi": 18000.0,
        "pro_forma_noi": 24000.0,
        "annual_debt_service": 12000.0,
        "annual_cash_flow": 6000.0,
        "total_cash_invested": 50000.0,
        "arv": 340000.0,
        "rehab_budget": 50000.0,
        "market_cap_rate": 0.07,
        "cash_flows": [-50000.0, 9000.0, 10000.0, 12000.0, 14000.0, 145000.0],
    }
