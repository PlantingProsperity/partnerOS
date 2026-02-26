from __future__ import annotations

from pathlib import Path

from partner_os.config import load_config
from partner_os.db.store import DataStore
from partner_os.models import AgentResult, Task, TaskType
from partner_os.services.queue import SequentialTaskQueue


def test_task_without_rationale_fails(tmp_path: Path):
    config = load_config(root_override=tmp_path)
    store = DataStore(config.database_path)

    store.create_deal(
        deal_id="deal-test",
        property_address="123 Main St, Vancouver, WA 98660",
        slug="123-main-st-vancouver-wa-98660",
        jurisdiction_warning=False,
    )

    queue = SequentialTaskQueue(store=store)

    def bad_handler(task: Task) -> AgentResult:  # noqa: ARG001
        return AgentResult(summary="done", rationale="")

    queue.register_handler(TaskType.create_deal_jacket, "Librarian", bad_handler)

    task = Task(
        task_id="task-1",
        task_type=TaskType.create_deal_jacket,
        deal_id="deal-test",
        actor="Manager",
        payload={"slug": "123-main-st-vancouver-wa-98660"},
        rationale="delegate",
    )
    queue.enqueue(task)
    result = queue.process_next()

    assert result is not None
    assert result.success is False

    task_row = store.get_task("task-1")
    assert task_row is not None
    assert task_row["status"] == "failed"

    action_logs = store.list_action_logs(limit=5)
    assert any("Task failed safely" in row["rationale"] for row in action_logs)

    store.close()
