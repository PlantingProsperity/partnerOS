from __future__ import annotations

import json


def test_end_to_end_pipeline(runtime_no_llm, default_cfo_payload):
    staged = runtime_no_llm.config.staging_inbox_dir / "seller_call.txt"
    staged.write_text(
        "Seller wants fast close due to relocation. Property: 789 Pine St, Vancouver, WA 98661.",
        encoding="utf-8",
    )

    result = runtime_no_llm.manager.handle_user_message(
        message="Start full analysis for 789 Pine St, Vancouver, WA 98661",
        uploaded_paths=[staged],
        cfo_payload=default_cfo_payload,
        run_scout=False,
    )

    deal_id = result["deal_id"]
    assert deal_id is not None

    deal = runtime_no_llm.store.get_deal(deal_id)
    assert deal is not None
    underwriting = json.loads(deal["underwriting_json"])
    assert underwriting["irr"] > 0
    assert "forced_equity_delta" in underwriting

    deal_root = runtime_no_llm.config.root_dir / f"{deal_id}_{deal['slug']}"
    deliverables = list((deal_root / "06_AI_Deliverables").glob("*.md"))
    assert any(path.name.startswith("cfo_underwriting_") for path in deliverables)

    inbox_text = runtime_no_llm.config.firm_inbox_path.read_text(encoding="utf-8")
    assert deal_id in inbox_text
    assert "Superintelligence Synthesis" in inbox_text

    action_logs = runtime_no_llm.store.list_action_logs(limit=200)
    assert action_logs
    assert all(str(log["rationale"]).strip() for log in action_logs)
