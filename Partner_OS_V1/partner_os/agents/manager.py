"""Manager agent: human interface and orchestration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from partner_os.agents.base import BaseAgent
from partner_os.constants import WA_TOKENS
from partner_os.models import AgentResult, Task, TaskType
from partner_os.services.filesystem import append_firm_inbox, deal_root, ensure_deal_jacket, newest_markdown_files
from partner_os.services.ids import new_deal_id, new_task_id, slugify
from partner_os.services.llm import GeminiAPIError, GeminiClient, NullLLMClient
from partner_os.services.queue import SequentialTaskQueue

ADDRESS_PATTERN = re.compile(
    r"(?P<address>\d{1,6}\s+[\w\s.-]+?,\s*[\w\s.-]+?,\s*(?:WA|OR|ID|Washington|Oregon|Idaho)\b[^\n]*)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class ManagerAgent(BaseAgent):
    queue: SequentialTaskQueue
    llm_client: GeminiClient | NullLLMClient

    def handle_user_message(
        self,
        message: str,
        uploaded_paths: list[Path],
        cfo_payload: dict[str, Any] | None = None,
        run_scout: bool = True,
    ) -> dict[str, Any]:
        """Create deal workflow from chat input and process queued tasks."""
        self.store.insert_chat_message(role="user", content=message)

        extracted_address = self._extract_address(message)
        if not extracted_address:
            response = (
                "No property address detected. Provide a full address like "
                "`123 Main St, Vancouver, WA 98663` to initialize a deal."
            )
            self.store.insert_chat_message(role="assistant", content=response)
            return {"deal_id": None, "response": response, "results": []}

        deal_id = new_deal_id()
        slug = slugify(extracted_address)
        jurisdiction_warning = not self._is_wa_address(extracted_address)

        self.store.create_deal(
            deal_id=deal_id,
            property_address=extracted_address,
            slug=slug,
            jurisdiction_warning=jurisdiction_warning,
        )
        self.store.log_action(
            actor=self.name,
            action="create_deal",
            rationale="Initialized new deal from chat context.",
            status="completed",
            deal_id=deal_id,
            details={"address": extracted_address, "jurisdiction_warning": jurisdiction_warning},
        )

        self._delegate(
            deal_id=deal_id,
            task_type=TaskType.create_deal_jacket,
            payload={"slug": slug},
            rationale="Initialize strict Deal Jacket before processing files.",
        )

        for upload_path in uploaded_paths:
            self._delegate(
                deal_id=deal_id,
                task_type=TaskType.triage_file,
                payload={
                    "staged_path": str(upload_path.resolve()),
                    "original_name": upload_path.name,
                },
                rationale="Route uploaded artifact from staging to mapped Deal Jacket folder.",
            )

        if run_scout:
            self._delegate(
                deal_id=deal_id,
                task_type=TaskType.run_scout,
                payload={"address": extracted_address},
                rationale="Generate advisory market context with citations for synthesis.",
            )

        if cfo_payload:
            self._delegate(
                deal_id=deal_id,
                task_type=TaskType.run_cfo,
                payload=cfo_payload,
                rationale="Execute deterministic CCIM underwriting for this deal.",
            )

        self._delegate(
            deal_id=deal_id,
            task_type=TaskType.append_firm_inbox,
            payload={"source": "manager_pipeline"},
            rationale="Append actionable summary for human review.",
        )

        results = self.queue.process_all()

        response = self._build_manager_reply(
            message=message,
            deal_id=deal_id,
            queue_results=[{"task_id": item.task_id, "success": item.success, "message": item.message} for item in results],
        )
        self.store.insert_chat_message(role="assistant", content=response, deal_id=deal_id)

        return {
            "deal_id": deal_id,
            "response": response,
            "results": results,
            "jurisdiction_warning": jurisdiction_warning,
        }

    def append_firm_inbox_task(self, task: Task) -> AgentResult:
        deal = self.store.get_deal(task.deal_id)
        if not deal:
            raise ValueError(f"Deal not found: {task.deal_id}")

        deal_path = ensure_deal_jacket(self.config, task.deal_id, deal["slug"])
        underwriting = json.loads(deal["underwriting_json"]) if deal["underwriting_json"] else {}

        market_files = newest_markdown_files(deal_path / "04_Intel_Docs", limit=1)
        market_excerpt = "No Scout report found."
        if market_files:
            market_excerpt = self._read_excerpt(market_files[0])

        cfo_files = newest_markdown_files(deal_path / "06_AI_Deliverables", limit=3)
        cfo_report = next((path for path in cfo_files if path.name.startswith("cfo_underwriting_")), None)

        warning_prefix = "[OUT OF STATE WARNING] " if int(deal["jurisdiction_warning"]) == 1 else ""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

        synthesis = self._build_synthesis(underwriting, market_excerpt)

        lines = [
            f"## {warning_prefix}{task.deal_id} - {deal['property_address']}",
            f"Time: `{timestamp}`",
            "",
            "### Status",
            f"- Deal Status: `{deal['status']}`",
            f"- Jurisdiction Warning: `{bool(int(deal['jurisdiction_warning']))}`",
            "",
            "### Deterministic Snapshot",
            f"- IRR: `{underwriting.get('irr', 'n/a')}`",
            f"- DSCR: `{underwriting.get('dscr', 'n/a')}`",
            f"- Cap Rate: `{underwriting.get('cap_rate', 'n/a')}`",
            f"- MAO: `{underwriting.get('mao', 'n/a')}`",
            f"- Forced Equity Delta: `{underwriting.get('forced_equity_delta', 'n/a')}`",
            "",
            "### Superintelligence Synthesis",
            synthesis,
            "",
            "### Artifacts",
            f"- CFO Report: `{cfo_report}`" if cfo_report else "- CFO Report: `not generated`",
            f"- Market Context: `{market_files[0]}`" if market_files else "- Market Context: `not generated`",
            "",
            "### Required Human Action",
            "- Review this summary and any draft deliverables before any external communication.",
            "",
        ]

        append_firm_inbox(self.config, "\n".join(lines))

        return AgentResult(
            summary="Appended actionable summary to 00_FIRM_INBOX.md",
            rationale="Delivered internal review package to human firewall queue.",
            details={"warning_prefix": warning_prefix.strip()},
        )

    def _delegate(self, deal_id: str, task_type: TaskType, payload: dict[str, Any], rationale: str) -> None:
        task = Task(
            task_id=new_task_id(),
            task_type=task_type,
            deal_id=deal_id,
            actor=self.name,
            payload=payload,
            rationale=rationale,
        )
        self.queue.enqueue(task)
        self.store.log_action(
            actor=self.name,
            action="delegate_task",
            rationale=rationale,
            status="queued",
            deal_id=deal_id,
            details={
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "payload": payload,
            },
        )

    def _build_manager_reply(self, message: str, deal_id: str, queue_results: list[dict[str, Any]]) -> str:
        transcript = [
            {"role": "user", "content": message},
            {"role": "system", "content": f"Queue results: {queue_results}"},
        ]
        try:
            return self.llm_client.chat_reply(transcript=transcript, deal_id=deal_id)
        except GeminiAPIError as exc:
            self.store.log_action(
                actor=self.name,
                action="chat_fallback",
                rationale="Gemini chat failed; deterministic fallback response returned.",
                status="completed",
                deal_id=deal_id,
                details={"error": str(exc)},
            )
            return (
                "Deal initialized and internal tasks processed. Gemini reply unavailable; "
                "review 00_FIRM_INBOX.md for actionable summary."
            )

    @staticmethod
    def _extract_address(message: str) -> str | None:
        match = ADDRESS_PATTERN.search(message)
        if not match:
            return None
        return re.sub(r"\s+", " ", match.group("address")).strip(" .")

    @staticmethod
    def _is_wa_address(address: str) -> bool:
        normalized = address.lower()
        return any(token in normalized for token in WA_TOKENS)

    @staticmethod
    def _read_excerpt(path: Path, limit: int = 700) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")[:limit].strip()
        except OSError:
            return "Unable to read report excerpt."

    @staticmethod
    def _build_synthesis(underwriting: dict[str, Any], market_excerpt: str) -> str:
        irr = underwriting.get("irr", "n/a")
        cap = underwriting.get("cap_rate", "n/a")
        forced_equity = underwriting.get("forced_equity_delta", "n/a")
        synthesis_lines = [
            (
                "- Deterministic core: "
                f"IRR `{irr}`, Cap Rate `{cap}`, Forced Equity Delta `{forced_equity}`."
            ),
            "- Advisory market pulse (Scout):",
            f"  {market_excerpt[:500]}",
            "- Action: validate assumptions against Firm Playbook before drafting external communication.",
        ]
        return "\n".join(synthesis_lines)
