"""Scout agent: advisory market intelligence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from partner_os.agents.base import BaseAgent
from partner_os.models import AgentResult, ScoutClaim, Task
from partner_os.services.filesystem import ensure_deal_jacket
from partner_os.services.search import WebSearchClient


@dataclass(slots=True)
class ScoutAgent(BaseAgent):
    search_client: WebSearchClient

    def run_market_scan_task(self, task: Task) -> AgentResult:
        deal = self.store.get_deal(task.deal_id)
        if not deal:
            raise ValueError(f"Deal not found: {task.deal_id}")

        property_address = deal["property_address"]
        query = (
            f"{property_address} Vancouver Clark County cap rate SOFR "
            "10-year treasury infrastructure zoning employers"
        )

        claims = self.search_client.search(query=query, limit=8)
        conflict_notes = self._detect_market_conflicts(claims)

        deal_root = ensure_deal_jacket(self.config, task.deal_id, deal["slug"])
        report_path = self._write_market_report(
            deal_root=deal_root,
            deal_id=task.deal_id,
            property_address=property_address,
            claims=claims,
            conflict_notes=conflict_notes,
        )

        return AgentResult(
            summary="Scout market intelligence report generated",
            rationale="Collected live web signals with citations and confidence labels.",
            details={
                "report_path": str(report_path),
                "claims_count": len(claims),
                "conflicts": conflict_notes,
            },
        )

    @staticmethod
    def _detect_market_conflicts(claims: list[ScoutClaim]) -> list[str]:
        cap_rates: list[float] = []
        rate_pattern = re.compile(r"(\d+(?:\.\d+)?)%")

        for claim in claims:
            if "cap" not in claim.summary.lower() and "cap" not in claim.title.lower():
                continue
            for match in rate_pattern.findall(claim.summary):
                cap_rates.append(float(match))

        if len(cap_rates) < 2:
            return []

        spread = max(cap_rates) - min(cap_rates)
        if spread >= 0.5:
            return [
                (
                    "Market Conflict: cap rate signals diverge by "
                    f"{spread:.2f}% across sources. Manual review required."
                )
            ]
        return []

    @staticmethod
    def _write_market_report(
        deal_root: Path,
        deal_id: str,
        property_address: str,
        claims: list[ScoutClaim],
        conflict_notes: list[str],
    ) -> Path:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = deal_root / "04_Intel_Docs" / f"market_context_{ts}.md"

        lines = [
            f"# Market Context Report ({deal_id})",
            "",
            f"Property: **{property_address}**",
            f"Generated: `{datetime.utcnow().isoformat()}Z`",
            "",
            "## Claims",
            "",
        ]

        if not claims:
            lines.extend([
                "No search claims returned.",
                "",
            ])

        for claim in claims:
            lines.extend(
                [
                    f"### {claim.title}",
                    f"- Confidence: **{claim.confidence_label} ({claim.confidence_score}%)**",
                    f"- Timestamp (UTC): `{claim.timestamp_utc}`",
                    f"- Source: {claim.url}",
                    f"- Summary: {claim.summary}",
                    "",
                ]
            )

        lines.extend([
            "## Market Conflicts",
            "",
        ])
        if conflict_notes:
            lines.extend([f"- {note}" for note in conflict_notes])
        else:
            lines.append("- None detected.")
        lines.append("")
        lines.extend(
            [
                "## Guidance",
                "",
                "Manager should treat this report as advisory and cross-check against Firm Playbook defaults.",
                "",
            ]
        )

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path
