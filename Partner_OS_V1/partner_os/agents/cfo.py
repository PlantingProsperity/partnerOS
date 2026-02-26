"""CFO agent: deterministic underwriting math."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from partner_os.agents.base import BaseAgent
from partner_os.models import AgentResult, CFOInput, Task
from partner_os.services.filesystem import ensure_deal_jacket


@dataclass(slots=True)
class CFOAgent(BaseAgent):
    """Deterministic underwriting engine."""

    def run_underwrite_task(self, task: Task) -> AgentResult:
        deal = self.store.get_deal(task.deal_id)
        if not deal:
            raise ValueError(f"Deal not found: {task.deal_id}")

        payload = task.payload
        cfo_input = CFOInput(
            purchase_price=float(payload["purchase_price"]),
            current_noi=float(payload["current_noi"]),
            pro_forma_noi=float(payload["pro_forma_noi"]),
            annual_debt_service=float(payload["annual_debt_service"]),
            annual_cash_flow=float(payload["annual_cash_flow"]),
            total_cash_invested=float(payload["total_cash_invested"]),
            arv=float(payload["arv"]),
            rehab_budget=float(payload["rehab_budget"]),
            market_cap_rate=float(payload["market_cap_rate"]),
            cash_flows=[float(item) for item in payload["cash_flows"]],
        )
        metrics = self.compute_metrics(cfo_input)

        self.store.update_deal_underwriting(task.deal_id, metrics)
        self.store.update_deal_status(task.deal_id, "underwritten")

        deal_root = ensure_deal_jacket(self.config, task.deal_id, deal["slug"])
        report_path = self._write_underwriting_report(deal_root, deal["property_address"], metrics)
        self.store.insert_document(
            deal_id=task.deal_id,
            category="06_AI_Deliverables",
            file_path=report_path,
            summary="Deterministic CFO underwriting report",
        )

        return AgentResult(
            summary="CFO underwriting complete",
            rationale="Computed CCIM metrics with deterministic formulas and persisted results.",
            details={"report_path": str(report_path), "metrics": metrics},
        )

    def compute_metrics(self, cfo_input: CFOInput) -> dict[str, float | str]:
        cap_rate = self.cap_rate(cfo_input.current_noi, cfo_input.purchase_price)
        dscr = self.dscr(cfo_input.current_noi, cfo_input.annual_debt_service)
        coc = self.cash_on_cash(cfo_input.annual_cash_flow, cfo_input.total_cash_invested)
        irr = self.irr(cfo_input.cash_flows)
        mao = self.mao(cfo_input.arv, cfo_input.rehab_budget)

        current_value = self.direct_cap_value(cfo_input.current_noi, cfo_input.market_cap_rate)
        stabilized_value = self.direct_cap_value(cfo_input.pro_forma_noi, cfo_input.market_cap_rate)
        forced_equity_delta = stabilized_value - cfo_input.purchase_price

        return {
            "irr": round(irr, 6),
            "dscr": round(dscr, 6),
            "cap_rate": round(cap_rate, 6),
            "cash_on_cash": round(coc, 6),
            "mao": round(mao, 2),
            "current_direct_capped_value": round(current_value, 2),
            "stabilized_direct_capped_value": round(stabilized_value, 2),
            "forced_equity_delta": round(forced_equity_delta, 2),
            "market_cap_rate": round(cfo_input.market_cap_rate, 6),
        }

    @staticmethod
    def cap_rate(noi: float, purchase_price: float) -> float:
        if purchase_price <= 0:
            raise ValueError("purchase_price must be > 0")
        return noi / purchase_price

    @staticmethod
    def dscr(noi: float, annual_debt_service: float) -> float:
        if annual_debt_service <= 0:
            raise ValueError("annual_debt_service must be > 0")
        return noi / annual_debt_service

    @staticmethod
    def cash_on_cash(annual_cash_flow: float, total_cash_invested: float) -> float:
        if total_cash_invested <= 0:
            raise ValueError("total_cash_invested must be > 0")
        return annual_cash_flow / total_cash_invested

    @staticmethod
    def direct_cap_value(noi: float, market_cap_rate: float) -> float:
        if market_cap_rate <= 0:
            raise ValueError("market_cap_rate must be > 0")
        return noi / market_cap_rate

    @staticmethod
    def mao(arv: float, rehab_budget: float, rule_pct: float = 0.7) -> float:
        return (arv * rule_pct) - rehab_budget

    @staticmethod
    def irr(cash_flows: list[float], low: float = -0.99, high: float = 10.0) -> float:
        if not cash_flows:
            raise ValueError("cash_flows cannot be empty")

        def npv(rate: float) -> float:
            total = 0.0
            for idx, cf in enumerate(cash_flows):
                total += cf / ((1 + rate) ** idx)
            return total

        low_npv = npv(low)
        high_npv = npv(high)
        if low_npv * high_npv > 0:
            return 0.0

        for _ in range(200):
            mid = (low + high) / 2
            mid_npv = npv(mid)
            if abs(mid_npv) < 1e-9:
                return mid
            if low_npv * mid_npv < 0:
                high = mid
                high_npv = mid_npv
            else:
                low = mid
                low_npv = mid_npv
        return (low + high) / 2

    @staticmethod
    def _write_underwriting_report(deal_root: Path, property_address: str, metrics: dict[str, float | str]) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = deal_root / "06_AI_Deliverables" / f"cfo_underwriting_{timestamp}.md"

        content = "\n".join(
            [
                f"# CFO Underwriting Report - {property_address}",
                "",
                "## Deterministic Metrics",
                "",
                f"- IRR: `{metrics['irr']}`",
                f"- DSCR: `{metrics['dscr']}`",
                f"- Cap Rate: `{metrics['cap_rate']}`",
                f"- Cash-on-Cash: `{metrics['cash_on_cash']}`",
                f"- MAO: `${metrics['mao']:,.2f}`",
                "",
                "## Direct Capped Analysis",
                "",
                f"- Market Cap Rate Input: `{metrics['market_cap_rate']}`",
                f"- Current Value: `${metrics['current_direct_capped_value']:,.2f}`",
                f"- Stabilized Value: `${metrics['stabilized_direct_capped_value']:,.2f}`",
                f"- Forced Equity Delta vs Purchase: `${metrics['forced_equity_delta']:,.2f}`",
                "",
                "## Raw JSON",
                "",
                "```json",
                json.dumps(metrics, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
        report_path.write_text(content, encoding="utf-8")
        return report_path
