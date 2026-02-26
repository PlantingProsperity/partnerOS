"""Utility CLI for initialization and smoke runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from partner_os.runtime import build_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Partner OS utility CLI")
    parser.add_argument("command", choices=["init", "status"], help="Command to run")
    args = parser.parse_args()

    runtime = build_runtime()

    if args.command == "init":
        runtime.librarian.index_firm_library()
        print("Initialized Partner OS runtime and indexed library.")
    elif args.command == "status":
        data = {
            "root": str(runtime.config.root_dir),
            "db": str(runtime.config.database_path),
            "deals": len(runtime.store.list_deals()),
            "tasks_pending": runtime.queue.pending_count,
            "action_logs": len(runtime.store.list_action_logs(limit=1000)),
        }
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
