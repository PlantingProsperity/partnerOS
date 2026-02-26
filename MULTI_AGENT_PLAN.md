# Multi-Agent Workflow Plan (Draft)

## Goal
Build an AI-native digital real estate back-office for a lean two-person team, optimized for speed, compliance, and repeatability. The Gemini-based Office Manager is the interface between the digital office and the two principals.

## Principles
- Automate low-leverage tasks first (intake, triage, routine comms, document generation).
- Keep human approvals on money/legal decisions.
- Use simple, auditable storage (Drive + versioned docs + event logs).
- Minimize infra overhead (no k8s, minimal DB unless needed).

## Agent Team (Minimal Viable Set)
The Office Manager can "hire" additional employees by creating new markdown role files with descriptions, responsibilities, and operating instructions. These files are loaded as new agent roles when added to the system.
1. Intake Agent
- Watches email/forms/Drive folders.
- Normalizes inputs into a single case record (JSON + human summary).
- Routes to triage.

2. Triage/Coordinator Agent
- Classifies incoming items (lead, tenant, maintenance, vendor, finance, legal).
- Sets priority and next best action.
- Assigns to specialist agents.

3. Tenant/Client Comms Agent
- Drafts and logs email/SMS responses.
- Uses templates, tone control, and approval required for sensitive content.
- Escalates when confidence is low or money/legal involved.

4. Docs & Forms Agent
- Generates leases, notices, invoices, letters.
- Pulls data from case record + templates.
- Outputs to Drive with versioning.

5. Finance Ops Agent
- Prepares invoices, reconciles data, generates monthly summaries.
- Suggest-only; human approval for any transactions.

6. Maintenance Ops Agent
- Converts issues into vendor requests and schedules.
- Tracks status updates and reminders.

7. Compliance/Review Agent
- Scans drafts for missing info, policy conflicts, risky language.
- Required sign-off for legal/financial docs.

## Tooling Map
- LLM: Gemini API (AI Studio key)
- Orchestration: codex CLI + python3 task runners
- Storage: rclone + rclone-drive.service for Drive sync and audit trail
- Messaging/Display (optional): catt + mkchromecast
- Containers (optional): podman for isolated services
- Search/Parsing: rg, httpx
- Version Control: git

## Data Model (Single Source of Truth)
A strict **Deal Schema** is the single source of truth and state persistence. All agents must read/write only through this schema. Case records can exist for non-deal operations but must link back to a deal when one exists.

### Deal Schema (Required)
- deal_id
- stage: lead | underwriting | offer | escrow | close | post_close
- status: active | paused | cancelled | closed
- priority: low | med | high
- parties: buyer, seller, agents, lenders, title, attorneys
- property: address, unit, owner, parcel_id
- financials: price, terms, deposits, fees, commissions
- dates: offer_date, acceptance_date, close_date, contingencies
- docs[]: offers, contracts, disclosures, addenda
- actions[]: actions with timestamps
- approvals[]: human approvals
- audit_log[]: immutable history of changes

### Case Schema (Non-deal)
- case_id
- type: tenant | maintenance | vendor | finance | legal | ops
- status: new | in_progress | waiting | resolved
- priority: low | med | high
- contact: name, phone, email
- property: address, unit, owner
- summary: LLM-generated
- raw_source: original email/form file
- actions[]: actions with timestamps
- artifacts[]: leases, invoices, notices, emails
- approvals[]: human approvals

## Example Flow (Maintenance Request)
1. Intake reads new request (email/form).
2. Triage tags maintenance, priority med, creates case.
3. Maintenance agent drafts vendor outreach + timeline.
4. Comms agent drafts tenant reply.
5. Compliance agent checks tone/risk/legal disclaimers.
6. Human approves.
7. Docs + Comms send; case updated.

## Guardrails (Strengthened)
- Human approval required for any money movement, legal notices, lease/eviction/notice docs, and compliance-sensitive text.
- Mandatory dual-review: Office Manager + Compliance/Review Agent for legal and financial outputs.
- Confidence thresholds: LLM must include a reasoning summary with citations from `deal_schema` fields or linked artifacts.
- Outbound drafts must be stored in Drive before sending; all outbound communications are logged.
- Sensitive data handling: redact PII where not required, minimal exposure to external tools, and explicit escalation for ambiguous cases.

## Implementation Roadmap (Expanded)
Phase 0: Policy + Schema
- Define strict Deal schema and Case schema with validation rules.
- Define role-based permissions and approval matrix.
- Define logging and audit retention policy.

Phase 1: Foundations (no OpenAI key needed)
- Drive folder structure: cases/, templates/, logs/, exports/, agents/
- Define and validate Deal/Case schemas + local JSON store
- Intake -> triage -> summary pipeline using Gemini
- Logging and audit trail for every agent action

Phase 2: Office Manager + Hiring System
- Office Manager role definition and prompt contract
- Agent role files in `agents/` (markdown-based hiring)
- Role loader to register new agents dynamically
- Guardrails enforcement layer (approvals + redaction)

Phase 3: Comms & Docs
- Template library (emails, invoices, notices, lease addenda)
- Comms agent with approval queue (drafts only)
- Docs agent with versioning and schema-backed fields

Phase 4: Ops Automation
- Maintenance queue, vendor management, reminders
- Finance summaries and reconciliation tools
- Vendor/tenant status dashboards

Phase 5: Multi-Agent Orchestration
- Role-based agents with explicit hand-offs and logs
- Inter-agent contracts and escalation paths
- Optional Podman services for always-on agents
