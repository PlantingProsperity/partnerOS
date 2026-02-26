from __future__ import annotations

from pathlib import Path


def test_librarian_moves_files_and_tracks_pointers(runtime_no_llm):
    staged = runtime_no_llm.config.staging_inbox_dir / "notes.txt"
    staged.write_text("Seller said roof leak and timeline 30 days.", encoding="utf-8")

    result = runtime_no_llm.manager.handle_user_message(
        message="New lead at 123 Main St, Vancouver, WA 98660",
        uploaded_paths=[staged],
        cfo_payload=None,
        run_scout=False,
    )

    deal_id = result["deal_id"]
    assert deal_id is not None

    deal = runtime_no_llm.store.get_deal(deal_id)
    assert deal is not None

    deal_root = runtime_no_llm.config.root_dir / f"{deal_id}_{deal['slug']}"
    moved_file = deal_root / "04_Intel_Docs" / "notes.txt"
    assert moved_file.exists()
    assert not staged.exists()

    docs = runtime_no_llm.store.list_documents(deal_id)
    doc_paths = {row["file_path"] for row in docs}
    assert str(moved_file) in doc_paths

    summary_files = list((deal_root / "06_AI_Deliverables").glob("notes_summary.md"))
    assert summary_files

    tasks = runtime_no_llm.store.list_tasks()
    assert tasks
    assert all(task["status"] == "completed" for task in tasks)
