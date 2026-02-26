"""Application runtime wiring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from partner_os.agents import CFOAgent, LibrarianAgent, ManagerAgent, ScoutAgent
from partner_os.config import AppConfig, load_config
from partner_os.db import DataStore
from partner_os.models import TaskType
from partner_os.services.filesystem import ensure_runtime_layout
from partner_os.services.llm import GeminiClient, NullLLMClient
from partner_os.services.queue import SequentialTaskQueue
from partner_os.services.search import WebSearchClient


@dataclass(slots=True)
class AppRuntime:
    config: AppConfig
    store: DataStore
    queue: SequentialTaskQueue
    manager: ManagerAgent
    librarian: LibrarianAgent
    cfo: CFOAgent
    scout: ScoutAgent

    def close(self) -> None:
        self.store.close()



def build_runtime(root_override: Path | None = None, use_llm: bool = True) -> AppRuntime:
    config = load_config(root_override=root_override)
    ensure_runtime_layout(config)

    store = DataStore(config.database_path)
    queue = SequentialTaskQueue(store=store)

    llm_client = GeminiClient(config=config, store=store) if use_llm else NullLLMClient()

    librarian = LibrarianAgent(name="Librarian", config=config, store=store, llm_client=llm_client)
    cfo = CFOAgent(name="CFO", config=config, store=store)
    scout = ScoutAgent(name="Scout", config=config, store=store, search_client=WebSearchClient())
    manager = ManagerAgent(name="Manager", config=config, store=store, queue=queue, llm_client=llm_client)

    queue.register_handler(TaskType.create_deal_jacket, "Librarian", librarian.create_deal_jacket_task)
    queue.register_handler(TaskType.triage_file, "Librarian", librarian.triage_staged_file_task)
    queue.register_handler(TaskType.run_cfo, "CFO", cfo.run_underwrite_task)
    queue.register_handler(TaskType.run_scout, "Scout", scout.run_market_scan_task)
    queue.register_handler(TaskType.append_firm_inbox, "Manager", manager.append_firm_inbox_task)

    return AppRuntime(
        config=config,
        store=store,
        queue=queue,
        manager=manager,
        librarian=librarian,
        cfo=cfo,
        scout=scout,
    )
