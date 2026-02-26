from __future__ import annotations


def test_gemini_failure_is_safe_and_logged(runtime_with_gemini):
    staged = runtime_with_gemini.config.staging_inbox_dir / "lead.txt"
    staged.write_text("Property has deferred maintenance and probate pressure.", encoding="utf-8")

    result = runtime_with_gemini.manager.handle_user_message(
        message="Please process 456 Oak Ave, Portland, OR 97201",
        uploaded_paths=[staged],
        cfo_payload=None,
        run_scout=False,
    )

    deal_id = result["deal_id"]
    assert deal_id is not None

    deal = runtime_with_gemini.store.get_deal(deal_id)
    assert deal is not None
    assert int(deal["jurisdiction_warning"]) == 1

    docs = runtime_with_gemini.store.list_documents(deal_id)
    assert docs

    api_calls = runtime_with_gemini.store.list_api_calls(limit=20)
    assert api_calls
    assert any(call["status"] == "failed" for call in api_calls)

    action_logs = runtime_with_gemini.store.list_action_logs(limit=50)
    assert any(log["action"] == "chat_fallback" for log in action_logs)

    inbox_text = runtime_with_gemini.config.firm_inbox_path.read_text(encoding="utf-8")
    assert "[OUT OF STATE WARNING]" in inbox_text
