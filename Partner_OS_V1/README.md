# Partner OS V1 (The Third Partner)

Partner OS V1 is a local-first AI operating system for real-estate deal intake, triage, underwriting, and internal drafting.

## V1 Scope

- Human interface: Streamlit chat with The Manager.
- Core active agents: Manager, Librarian, CFO.
- Advisory specialist: Scout (read-only market intelligence).
- Storage: local SQLite (`firm_intelligence.db`) + strict Deal Jacket filesystem.
- Airgap: no outbound communication integrations (draft-only outputs).

## Directory Contract

- `_STAGING_INBOX/`: temporary upload inbox.
- `00_FIRM_INBOX.md`: human escalation and review queue.
- `00_FIRM_LIBRARY/`: read-only doctrine/reference documents.
- `[deal_id]_[property_address]/`
  - `01_Intel_Photos/`
  - `02_Intel_Video/`
  - `03_Intel_Audio/`
  - `04_Intel_Docs/`
  - `05_System_State/`
  - `06_AI_Deliverables/`

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy env file and set Gemini key:

```bash
cp .env.example .env
```

4. Run the Streamlit app:

```bash
streamlit run app.py
```

5. Run tests:

```bash
pytest -q
```

## Reliability Rules

- SQLite runs in WAL mode.
- Sequential worker queue only.
- Every automated action requires a non-empty rationale in `action_logs`.
- Gemini API failures must fail-safe without corrupting deal state.
