from __future__ import annotations

import math

from partner_os.agents.cfo import CFOAgent
from partner_os.config import load_config
from partner_os.db.store import DataStore
from partner_os.models import CFOInput


def _agent(tmp_path):
    config = load_config(root_override=tmp_path)
    store = DataStore(config.database_path)
    return CFOAgent(name="CFO", config=config, store=store), store


def test_cfo_deterministic_metrics(tmp_path):
    agent, store = _agent(tmp_path)
    cfo_input = CFOInput(
        purchase_price=250000,
        current_noi=18000,
        pro_forma_noi=24000,
        annual_debt_service=12000,
        annual_cash_flow=6000,
        total_cash_invested=50000,
        arv=340000,
        rehab_budget=50000,
        market_cap_rate=0.07,
        cash_flows=[-50000, 9000, 10000, 12000, 14000, 145000],
    )

    metrics = agent.compute_metrics(cfo_input)

    assert metrics["cap_rate"] == pytest_approx(0.072)
    assert metrics["dscr"] == pytest_approx(1.5)
    assert metrics["cash_on_cash"] == pytest_approx(0.12)
    assert metrics["mao"] == pytest_approx(188000.0)
    assert metrics["current_direct_capped_value"] == pytest_approx(257142.86)
    assert metrics["stabilized_direct_capped_value"] == pytest_approx(342857.14)
    assert metrics["forced_equity_delta"] == pytest_approx(92857.14)
    assert metrics["irr"] > 0

    store.close()


def test_irr_known_result(tmp_path):
    agent, store = _agent(tmp_path)
    irr = agent.irr([-1000, 300, 400, 500])
    assert math.isclose(irr, 0.088963, rel_tol=1e-3)
    store.close()


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, rel=1e-4, abs=1e-4)
