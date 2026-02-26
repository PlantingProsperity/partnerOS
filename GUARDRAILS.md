# Guardrails And Safety Policy (The Safety Cage)

## Goal
Allow the Office Manager and sub-agents to operate autonomously on low-risk tasks while strictly preventing financial loss, legal liability, or reputational damage.

## Financial Autonomy (Zero-Trust Model)
- Emergency maintenance limit: $0.00.
- Action: Agent must text or call both principals immediately.
- Escalation: If no response in 1 hour and severity is `Critical` (e.g., active flood), the agent drafts a dispatch request for the Emergency Vendor but awaits 1-click confirmation.
- Operational spend limit: $0.00.
- Action: All software, ads, or service fees must be queued in `Finance_Ops` for human approval.
- Money movement:
- Agents are blocked from bank logins, wire platforms, or check-writing tools.
- Agents may prepare invoices or check requests, but a human must execute any transaction.

## Communication Guardrails (The Outbox Rule)
- Draft-only mode (email):
- All client, tenant, or agent emails are saved as drafts in Gmail.
- Exception: Routine confirmations (e.g., "Request Received") may be auto-sent if strictly templated.
- No-send policy (SMS/text):
- Agents are strictly prohibited from sending SMS directly.
- Mechanism: Agent records suggested SMS text in the `interaction_log` or a notification channel.
- Action: Human principal must manually copy and send the text.
- Consent verification:
- No outbound marketing or SMS may be drafted unless `marketing_consent` is true and `do_not_contact` is false in the lead record.
- Tone and legal check:
- All drafts must pass a Compliance Agent scan for prohibited language (e.g., Fair Housing violations such as "family-friendly" or "bachelor pad").
- Failure: Draft is flagged `NEEDS_REVISION` and assigned to a human.

## Data Privacy And Access
- PII redaction:
- SSNs, bank account numbers, and driver’s license scans are never passed into the LLM context window.
- Protocol: Agents reference sensitive files by `file_id` only (e.g., "DL_Scan.pdf") unless explicitly authorized for a specific OCR task.
- Credential isolation:
- No API keys, passwords, or login tokens are stored in plain text in agent instructions.
- Agents use environment variables or secure vaults only.

## Operational Circuit Breakers
- Loop detection: If an agent fails a task 3 times in a row, the Case status flips to `Review` (human intervention) to prevent API cost runaways.
- Hallucination check: Every factual assertion (e.g., "Tenant paid on 5th") must cite a specific `event_id` or `doc_id` from the single source of truth (`DEAL_SCHEMA` or `CASE_SCHEMA`).

## Human-in-the-Loop Approval Matrix
| Risk Level | Examples | Required Approval |
| :--- | :--- | :--- |
| Low | Sorting email, logging leads, drafting internal notes | None (Autonomous) |
| Medium | Drafting tenant replies, scheduling inspections | Post-Action Notify (Weekly Log) |
| High | Sending offers, posting listings, lease notices | Pre-Action Approval (1-Click) |
| Critical | Spending money, legal settlements, evictions | Dual Approval (Both Partners) |

## Data Retention And Lifecycle
- Business intelligence (keep forever):
- All Deal and Case records, interaction logs, and decision summaries are retained indefinitely to build long-term investment knowledge.
- Compliance files (keep forever):
- All executed contracts and disclosures are retained indefinitely (exceeding WA State 3-year minimum).
- Liability purge (the shredder):
- Files tagged `#PII` (credit reports, driver’s license scans, unredacted bank statements) are flagged for deletion or redaction 30 days after Deal Closing or Case Resolution.
- Safety check: The Office Manager cannot delete these files; they are moved to a "To-Shred" folder for human confirmation.

## Jurisdiction Lock (Washington State Only)
- Default scope: Washington State (WA).
- Blocking rule:
- If `property_address` state is not "WA" or "Washington":
- Action: Agent is blocked from selecting forms, drafting contracts, or offering compliance advice.
- Status: Case flips to `Review` (human intervention required for referral).
- Forms library: Restricted to NWMLS forms only.

## Licensed Activity And Scope (The Unlicensed Assistant Rule)
- Legal status: The Office Manager and all sub-agents operate as unlicensed assistants.
- Hard blocks (requires principal action):
- Signing: Agents are prohibited from applying digital signatures to any binding contract.
- Negotiation: Agents cannot negotiate terms. They may only transmit verbatim offers or counters drafted by the principals.
- Legal advice: Agents must never interpret contract law or offer legal opinions.
- Trigger response: If a client asks "What does this clause mean?", the agent replies with a template: "I am an automated assistant. Please hold for Dan or Roman to provide professional guidance on this contract term."

## Vendor Vetting And Dispatch
- Approved vendors (whitelist):
- Agents may draft work orders only for vendors listed in `approved_vendors.json`.
- New vendor sourcing:
- Agents may research new vendors but cannot dispatch them.
- Action: Agent presents vendor license, bond, and insurance info to the principals.
- Approval: A human must add the vendor to `approved_vendors.json` before they can be assigned to a Case.

## PSA And Contract Drafting Protocol (The No Guessing Rule)
- Strict input:
- Agents populate NWMLS forms only using explicit data present in the Deal record.
- No inference:
- If a term is missing (e.g., Closing Date, Title Company), the agent is forbidden from guessing defaults.
- Action: Agent must flag the missing field and request user input.
- Watermarking:
- All AI-generated contract drafts must use the filename suffix `_DRAFT_AI_REVIEW_REQ` until approved by a principal.

## Client Verification And Anti-Fraud
- Known contacts only:
- Agents may only send documents to email addresses and phone numbers explicitly listed in the Deal or Lead record.
- Trigger:
- If a message comes from a new address claiming to be the client, the agent is blocked and must flag for human verification.
- No wire instructions:
- Agents are prohibited from generating, sending, or confirming wire instructions.
- Auto-reply:
- If a client asks where to wire EMD, the agent replies with a template directing them to the Escrow Officer only.

## Knowledge Base Authority (Strategy And Advice)
- Facts:
- Must cite Deal or Case records (e.g., "Rent is $1,500").
- Strategy and philosophy:
- Must cite Pinneo_Library or Weichert_Manual (e.g., "Greg says never buy based on appreciation alone").
- Prohibited:
- Generic LLM training data is banned for strategic advice.

## Enforcement Mechanisms
- Layer 1: System Prompt (soft enforcement):
- All rules regarding tone, strategy, and no guessing are injected into the agent's system instructions.
- Layer 2: Middleware and code (hard enforcement):
- PII scanner: A regex filter runs on all outbound text; if SSN or credit card patterns are found, the action is blocked.
- State lock: A Python check verifies `property_address.state == "WA"` before allowing form selection.
- Spend limit: The finance handler throws a hard exception if `amount > $0.00`.
- Layer 3: Human gateway (the air gap):
- All High and Critical risk actions result in a STOP status and land in a review queue.
- The action cannot proceed until a human authorization token is provided.

## Incident Response (The Big Red Button)
- Emergency stop command (`/FREEZE`):
- Trigger: Principal issues `/FREEZE`.
- Action: All agent queues paused. API tokens revoked temporarily. System enters `Safe_Mode` (read-only).
- Data leak protocol:
- Trigger: PII detected in outbound log post-transmission.
- Action: System auto-locks. Immediate SMS alert to principals. Incident log created.
- Suspected fraud:
- Trigger: Failed DKIM or SPF checks, or phishing keywords.
- Action: Sender blocked. Case flagged `Potential_Fraud`.
