# Implementation Roadmap

We have the Blueprints (Schemas), the Laws (Guardrails), and the Team (Agents). Now we need the construction plan.

## Phase 1: The "Analyzer" Engine (Valuation & Logic)
**Goal:** Input an address -> Output a decision (Buy/Pass/Counter).
**Focus:** `ANALYSIS_SCHEMA`, `GUARDRAILS` (Financial).
1. **Build The Scout.** Script: Scrape/fetch basic property specs (sq ft, year built, lot size). Output: Populates valuation baselines used in `ANALYSIS_SCHEMA`.
2. **Build The Planner.** Script: Check zoning code against allowable uses table. Output: Populates `ANALYSIS_SCHEMA` development potential.
3. **Build The Underwriter.** Script: Run the "Pinneo Math" (MAO = ARV * 0.7 - Rehab). Output: Generates `target_offer_price` and `exit_strategy`.
4. **Deliverable.** A CLI tool where you type `analyze 123 Main St` and get a Markdown report with a Green/Red light.

## Phase 2: The "Intake" Engine (Lead Capture)
**Goal:** Raw text/email -> Structured lead.
**Focus:** `LEAD_SCHEMA`, `AGENT_ROSTER` (The Manager).
1. **Build The Manager (Triage).** Script: Parse incoming emails/texts for contact info and intent. Action: Create `LEAD_SCHEMA` entry or link to existing.
2. **Build The Scout (Enrichment).** Script: Auto-search the seller to find motivation clues (e.g., obituary). Output: Populates `LEAD_SCHEMA.motivation_score`.
3. **Deliverable.** An "Inbox Watcher" that turns a forwarded email into a database row automatically.

## Phase 3: The "Compliance" Engine (Ops & Safety)
**Goal:** Chaos -> Order.
**Focus:** `CASE_SCHEMA`, `GUARDRAILS` (Legal/Data).
1. **Build The Librarian.** Script: Rename and move PDF attachments to `/deals/{id}/contracts/`.
2. **Build The Janitor.** Script: Scan for missing docs (e.g., "Missing Form 17") and alert The Manager.
3. **Deliverable.** A "Nightly Audit" report showing exactly which files are missing for every active deal.
