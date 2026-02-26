"""Streamlit UI for Partner OS V1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from partner_os.runtime import AppRuntime, build_runtime


@st.cache_resource
def get_runtime() -> AppRuntime:
    return build_runtime()



def stage_uploads(runtime: AppRuntime, uploads: list[Any]) -> list[Path]:
    staged_paths: list[Path] = []
    for upload in uploads:
        target = runtime.config.staging_inbox_dir / upload.name
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            counter = 1
            while True:
                candidate = target.with_name(f"{stem}_{counter}{suffix}")
                if not candidate.exists():
                    target = candidate
                    break
                counter += 1
        target.write_bytes(upload.getbuffer())
        staged_paths.append(target)
    return staged_paths



def build_cfo_payload() -> dict[str, Any]:
    return {
        "purchase_price": st.session_state.get("purchase_price", 250000.0),
        "current_noi": st.session_state.get("current_noi", 18000.0),
        "pro_forma_noi": st.session_state.get("pro_forma_noi", 24000.0),
        "annual_debt_service": st.session_state.get("annual_debt_service", 12000.0),
        "annual_cash_flow": st.session_state.get("annual_cash_flow", 6000.0),
        "total_cash_invested": st.session_state.get("total_cash_invested", 50000.0),
        "arv": st.session_state.get("arv", 340000.0),
        "rehab_budget": st.session_state.get("rehab_budget", 50000.0),
        "market_cap_rate": st.session_state.get("market_cap_rate", 0.07),
        "cash_flows": [
            st.session_state.get("cf_0", -50000.0),
            st.session_state.get("cf_1", 9000.0),
            st.session_state.get("cf_2", 10000.0),
            st.session_state.get("cf_3", 12000.0),
            st.session_state.get("cf_4", 14000.0),
            st.session_state.get("cf_5", 145000.0),
        ],
    }



def render_sidebar(runtime: AppRuntime) -> tuple[list[Any], bool, bool]:
    st.sidebar.header("Partner Activity")
    st.sidebar.write(f"Status: **{runtime.queue.current_activity}**")
    st.sidebar.write(f"Pending Tasks: **{runtime.queue.pending_count}**")

    if st.sidebar.button("Index 00_FIRM_LIBRARY"):
        result = runtime.librarian.index_firm_library()
        runtime.store.log_action(
            actor="Librarian",
            action="index_firm_library",
            rationale=result.rationale,
            status="completed",
            details=result.details,
        )
        st.sidebar.success(result.summary)

    uploads = st.sidebar.file_uploader(
        "Upload files for active chat context",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "mp4", "mov", "mp3", "wav", "pdf", "doc", "docx", "txt", "md"],
    )
    include_cfo = st.sidebar.checkbox("Run CFO underwrite", value=True)
    include_scout = st.sidebar.checkbox("Run Scout market pulse", value=True)

    with st.sidebar.expander("CFO Inputs"):
        st.number_input("Purchase Price", key="purchase_price", value=250000.0)
        st.number_input("Current NOI", key="current_noi", value=18000.0)
        st.number_input("Pro Forma NOI", key="pro_forma_noi", value=24000.0)
        st.number_input("Annual Debt Service", key="annual_debt_service", value=12000.0)
        st.number_input("Annual Cash Flow", key="annual_cash_flow", value=6000.0)
        st.number_input("Total Cash Invested", key="total_cash_invested", value=50000.0)
        st.number_input("ARV", key="arv", value=340000.0)
        st.number_input("Rehab Budget", key="rehab_budget", value=50000.0)
        st.number_input("Market Cap Rate", key="market_cap_rate", value=0.07, step=0.005, format="%.4f")
        for idx, default in enumerate([-50000.0, 9000.0, 10000.0, 12000.0, 14000.0, 145000.0]):
            st.number_input(f"Cash Flow Year {idx}", key=f"cf_{idx}", value=default)

    return uploads, include_cfo, include_scout



def render_chat(runtime: AppRuntime) -> None:
    st.title("Partner OS - The Manager")

    for row in runtime.store.list_chat_messages(limit=200):
        with st.chat_message(row["role"]):
            st.markdown(row["content"])



def render_panels(runtime: AppRuntime) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("00_FIRM_INBOX.md")
        st.code(runtime.config.firm_inbox_path.read_text(encoding="utf-8"), language="markdown")

    with col2:
        st.subheader("Recent action_logs")
        logs = runtime.store.list_action_logs(limit=20)
        if not logs:
            st.write("No audit entries yet.")
        else:
            for row in logs:
                st.markdown(
                    "\n".join(
                        [
                            f"**[{row['timestamp']}] {row['actor']}** - `{row['action']}` ({row['status']})",
                            f"Rationale: {row['rationale']}",
                            "",
                        ]
                    )
                )



def main() -> None:
    runtime = get_runtime()
    uploads, include_cfo, include_scout = render_sidebar(runtime)
    render_chat(runtime)

    message = st.chat_input("Message The Manager")
    if message:
        staged = stage_uploads(runtime, uploads or [])
        cfo_payload = build_cfo_payload() if include_cfo else None

        try:
            result = runtime.manager.handle_user_message(
                message=message,
                uploaded_paths=staged,
                cfo_payload=cfo_payload,
                run_scout=include_scout,
            )
            st.session_state["last_result"] = {
                "deal_id": result["deal_id"],
                "response": result["response"],
                "results": [
                    {"task_id": item.task_id, "success": item.success, "message": item.message}
                    for item in result["results"]
                ],
            }
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Manager pipeline failed safely: {exc}")

    if "last_result" in st.session_state:
        st.subheader("Last Pipeline Result")
        st.json(st.session_state["last_result"])

    render_panels(runtime)


if __name__ == "__main__":
    main()
