"""Single-worker sequential queue for agent tasks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable

from partner_os.db.store import DataStore
from partner_os.models import AgentResult, Task, TaskStatus, TaskType

TaskHandler = Callable[[Task], AgentResult]


@dataclass(slots=True)
class QueueExecutionResult:
    task_id: str
    success: bool
    message: str


class SequentialTaskQueue:
    """FIFO queue with one-at-a-time execution."""

    def __init__(self, store: DataStore):
        self.store = store
        self._queue: deque[Task] = deque()
        self._handlers: dict[TaskType, tuple[str, TaskHandler]] = {}
        self.current_activity: str = "Idle"

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    def register_handler(self, task_type: TaskType, agent_name: str, handler: TaskHandler) -> None:
        self._handlers[task_type] = (agent_name, handler)

    def enqueue(self, task: Task) -> None:
        self.store.insert_task(
            task_id=task.task_id,
            deal_id=task.deal_id,
            task_type=task.task_type.value,
            payload=task.payload,
            status=TaskStatus.queued.value,
        )
        self._queue.append(task)

    def process_next(self) -> QueueExecutionResult | None:
        if not self._queue:
            self.current_activity = "Idle"
            return None

        task = self._queue.popleft()
        if task.task_type not in self._handlers:
            raise ValueError(f"No handler registered for task type {task.task_type}.")

        agent_name, handler = self._handlers[task.task_type]
        self.current_activity = f"{agent_name} is processing {task.task_type.value}"

        self.store.update_task_status(task.task_id, TaskStatus.running.value)
        run_id = self.store.create_agent_run(
            task_id=task.task_id,
            deal_id=task.deal_id,
            agent_name=agent_name,
            payload=task.payload,
        )

        try:
            with self.store.transaction():
                result = handler(task)
                if not result.rationale or not result.rationale.strip():
                    raise ValueError("Task completed without rationale.")

                self.store.finish_agent_run(
                    run_id=run_id,
                    status=TaskStatus.completed.value,
                    output={"summary": result.summary, "details": result.details},
                )
                self.store.update_task_status(task.task_id, TaskStatus.completed.value)
                self.store.log_action(
                    actor=agent_name,
                    action=task.task_type.value,
                    rationale=result.rationale,
                    status=TaskStatus.completed.value,
                    deal_id=task.deal_id,
                    details={
                        "task_id": task.task_id,
                        "summary": result.summary,
                        "details": result.details,
                    },
                )
            return QueueExecutionResult(task_id=task.task_id, success=True, message=result.summary)
        except Exception as exc:  # noqa: BLE001
            self.store.finish_agent_run(
                run_id=run_id,
                status=TaskStatus.failed.value,
                output={"error": str(exc)},
            )
            self.store.update_task_status(task.task_id, TaskStatus.failed.value)
            self.store.log_action(
                actor=agent_name,
                action=task.task_type.value,
                rationale=f"Task failed safely: {exc}",
                status=TaskStatus.failed.value,
                deal_id=task.deal_id,
                details={"task_id": task.task_id},
            )
            return QueueExecutionResult(task_id=task.task_id, success=False, message=str(exc))
        finally:
            self.current_activity = "Idle"

    def process_all(self) -> list[QueueExecutionResult]:
        results: list[QueueExecutionResult] = []
        while self._queue:
            result = self.process_next()
            if result is not None:
                results.append(result)
        self.current_activity = "Idle"
        return results
