"""Librarian agent: triage and indexing."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from partner_os.agents.base import BaseAgent
from partner_os.constants import EXTENSION_TO_SUBDIR, is_within_directory
from partner_os.models import AgentResult, Task
from partner_os.services.filesystem import ensure_deal_jacket
from partner_os.services.llm import GeminiAPIError, GeminiClient, NullLLMClient


@dataclass(slots=True)
class LibrarianAgent(BaseAgent):
    llm_client: GeminiClient | NullLLMClient

    def create_deal_jacket_task(self, task: Task) -> AgentResult:
        deal = self.store.get_deal(task.deal_id)
        if not deal:
            raise ValueError(f"Deal not found: {task.deal_id}")

        deal_root = ensure_deal_jacket(self.config, task.deal_id, deal["slug"])
        self.store.log_action(
            actor=self.name,
            action="create_deal_jacket",
            rationale="Initialized strict Deal Jacket directory contract.",
            status="completed",
            deal_id=task.deal_id,
            details={"deal_root": str(deal_root)},
        )
        return AgentResult(
            summary=f"Deal Jacket ready at {deal_root}",
            rationale="Created required folder boundaries before file writes.",
            details={"deal_root": str(deal_root)},
        )

    def triage_staged_file_task(self, task: Task) -> AgentResult:
        deal = self.store.get_deal(task.deal_id)
        if not deal:
            raise ValueError(f"Deal not found: {task.deal_id}")

        staged_path = Path(task.payload["staged_path"]).resolve()
        original_name = task.payload.get("original_name", staged_path.name)
        if not staged_path.exists():
            raise FileNotFoundError(f"Staged file missing: {staged_path}")
        if not is_within_directory(self.config.staging_inbox_dir, staged_path):
            raise ValueError("Staged file is outside of _STAGING_INBOX contract.")

        deal_root = ensure_deal_jacket(self.config, task.deal_id, deal["slug"])
        ext = staged_path.suffix.lower()
        subdir_name = EXTENSION_TO_SUBDIR.get(ext, "04_Intel_Docs")
        target_dir = deal_root / subdir_name
        target_path = self._unique_target_path(target_dir / original_name)

        moved = False
        try:
            staged_path.replace(target_path)
            moved = True

            summary_text, fallback = self._summarize_file(task.deal_id, target_path)
            summary_md = self._write_summary_file(deal_root=deal_root, file_path=target_path, summary=summary_text)

            self.store.insert_document(
                deal_id=task.deal_id,
                category=subdir_name,
                file_path=target_path,
                summary=summary_text,
            )
            self.store.insert_document(
                deal_id=task.deal_id,
                category="06_AI_Deliverables",
                file_path=summary_md,
                summary="Librarian artifact summary",
            )

            self.store.log_action(
                actor=self.name,
                action="file_move",
                rationale="Moved staged artifact into strict Deal Jacket destination.",
                status="completed",
                deal_id=task.deal_id,
                details={
                    "from": str(staged_path),
                    "to": str(target_path),
                    "fallback_summary": fallback,
                },
            )

            return AgentResult(
                summary=f"Triaged {original_name} -> {subdir_name}",
                rationale="Validated extension map and preserved filesystem pointer integrity.",
                details={
                    "target_path": str(target_path),
                    "summary_path": str(summary_md),
                },
            )
        except Exception:
            if moved and target_path.exists():
                target_path.replace(self.config.staging_inbox_dir / target_path.name)
            raise

    def index_firm_library(self) -> AgentResult:
        indexed = 0
        for path in sorted(self.config.firm_library_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
                continue

            digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]
            ref_id = f"lib-{digest}"
            content = self._read_text_excerpt(path)
            abstract = self._safe_library_abstract(content)
            self.store.upsert_library_entry(
                ref_id=ref_id,
                title=path.stem,
                file_path=path,
                doctrine_abstract=abstract,
            )
            indexed += 1

        return AgentResult(
            summary=f"Indexed {indexed} library files",
            rationale="Maintained global doctrine index for Manager retrieval.",
            details={"indexed": indexed},
        )

    def _safe_library_abstract(self, content: str) -> str:
        if not content.strip():
            return "No parseable text detected."
        try:
            return self.llm_client.summarize_text(content[:5000], deal_id=None)
        except GeminiAPIError:
            return content[:400].strip()

    def _summarize_file(self, deal_id: str, file_path: Path) -> tuple[str, bool]:
        text_excerpt = self._read_text_excerpt(file_path)
        if not text_excerpt:
            return (
                "Binary or non-text artifact. Manual review required. \n"
                f"File: {file_path.name} ({file_path.suffix.lower()})",
                True,
            )

        try:
            summary = self.llm_client.summarize_text(text_excerpt[:9000], deal_id=deal_id)
            return summary, False
        except GeminiAPIError as exc:
            self.store.log_action(
                actor=self.name,
                action="summary_fallback",
                rationale="Gemini summary failed; fallback summary preserved pipeline continuity.",
                status="completed",
                deal_id=deal_id,
                details={"error": str(exc), "file": str(file_path)},
            )
            fallback = "\n".join(
                [
                    "LLM summary unavailable. Fallback excerpt:",
                    text_excerpt[:600].strip() or "No textual content.",
                ]
            )
            return fallback, True

    @staticmethod
    def _read_text_excerpt(path: Path) -> str:
        if path.suffix.lower() not in {".txt", ".md", ".csv", ".json"}:
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    @staticmethod
    def _unique_target_path(target: Path) -> Path:
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        counter = 1
        while True:
            candidate = target.with_name(f"{stem}_{counter}{suffix}")
            if not candidate.exists():
                return candidate
            counter += 1

    @staticmethod
    def _write_summary_file(deal_root: Path, file_path: Path, summary: str) -> Path:
        deliverable = deal_root / "06_AI_Deliverables" / f"{file_path.stem}_summary.md"
        content = "\n".join(
            [
                f"# Librarian Summary: {file_path.name}",
                "",
                f"Source: `{file_path}`",
                "",
                summary.strip(),
                "",
            ]
        )
        deliverable.write_text(content, encoding="utf-8")
        return deliverable
