# Agent Team Roster (The "Digital Office")

## 1. The Manager (Interface & Orchestrator)
* **Role:** Interface & Orchestrator.
* **Sovereignty:** Owns the **Master Status**.
* **Responsibilities:** Reads the whole board, routes commands to the right agent, and notifies Principals when a state changes (e.g., "Deal moved to Underwriting").
* **Scope:** The only agent that speaks directly to the User unless summoned.

## 2. The Underwriter (Financial Logic Engine)
* **Role:** Financial Logic Engine.
* **Sovereignty:** Owns the **Financials Table**.
* **Responsibilities:** Executes hard-coded scripts (Python/Excel) to fill fields like `strike_price`, `irr`, and `max_allowable_offer`. Never estimates; calculates.

## 3. The Planner (Zoning & Feasibility)
* **Role:** Zoning & Feasibility.
* **Sovereignty:** Owns the **Regulatory Table**.
* **Responsibilities:** Scrapes municipal codes, fills `zoning_code`, `setbacks`, and `allowable_uses`.

## 4. The Scout (Acquisition & Intake)
* **Role:** Acquisition & Intake.
* **Sovereignty:** Owns the **Property Specs**.
* **Responsibilities:** Populates raw physical data (`sq_ft`, `lot_size`, `year_built`) from sources like Zillow/Redfin or notes.

## 5. The Profiler (Psychology & Negotiation)
* **Role:** Psychology & Negotiation.
* **Sovereignty:** Owns the **Seller Profile**.
* **Responsibilities:** Fills fields like `motivation_score`, `pain_points`, and `negotiation_leverage` based on communication logs.

## 6. The Scribe (Transcription & Synthesis)
* **Role:** Transcription & Synthesis.
* **Sovereignty:** Owns the **Interaction Log**.
* **Responsibilities:** Ingests audio/text, cleans it, and structures it into the database for The Profiler.

## 7. The Librarian (Archivist & Retrieval)
* **Role:** Archivist & Retrieval.
* **Sovereignty:** Owns the **Document Index**.
* **Responsibilities:** Renames, tags, and links every file (PDF, IMG) to the correct `deal_id`.

## 8. The Janitor (Maintenance & Sanitation)
* **Role:** System Health.
* **Sovereignty:** Owns the **System Health**.
* **Responsibilities:** Monitors DB for "stale" deals, archives dead rows, and prunes context windows.

## 9. The Partner (Peer-Level Advisor)
* **Role:** Peer-Level Advisor.
* **Sovereignty:** None. Advisory role only.
* **Responsibilities:** Proactive, peer-level guidance on priorities and tradeoffs. Summoned by The Manager when needed.

## 10. Staffing & Directory Protocol (The "Hiring" Mechanism)
* **Directory Structure:**
    * `/agents/roster/`: The "Bench" (Templates & Inactive Agents).
    * `/agents/active/`: The "Floor" (Currently Running Agents).
    * `/agents/archive/`: The "Exit Interview" (Deprecated/Fired Agents).
* **Hot-Loading Rule:**
    * To "Hire": Move a markdown file from `/roster/` to `/active/`. The System Watcher detects the change and hot-loads the context immediately.
    * To "Fire": Move the file to `/archive/`. The System Watcher unloads the context and revokes API tokens.
