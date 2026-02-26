# Case Schema (Operations)

## Goal
Provide a unified lifecycle and schema for all non-deal operational work. This keeps the Office Manager inbox logic consistent while allowing case-specific context via optional objects.

## Case Types (Enum)
- `Maintenance`: Physical repairs, CapEx projects, turnover work.
- `Tenant_Request`: Non-repair issues, lease questions, complaints.
- `Vendor_Job`: Bidding, scheduling, insurance compliance.
- `Finance_Ops`: Invoices to pay, bookkeeping queries, tax prep.
- `Compliance_Review`: File audits, license renewals, CE tracking.
- `Marketing_Task`: Social media posts, mailer campaigns, lead gen prep.

## Unified Status Lifecycle (Enum)
- `New`: Raw intake, unassigned.
- `Triage`: Classified, prioritized, and assigned.
- `In_Progress`: Active work being done.
- `Blocked`: Waiting on outside input (parts, vendor reply, tenant access).
- `Review`: Work done, waiting for final sign-off (Manager or Principal).
- `Resolved`: Completed and archived.

## Universal Required Fields
- `case_id`: UUID.
- `linked_deal_id`: Nullable (link to Deal if applicable).
- `linked_property_id`: Nullable (link to specific asset).
- `priority`: Enum [Low, Normal, High, Critical].
- `severity`: Enum [Cosmetic, Functional, Urgent, Emergency] (default: Functional).
- `assigned_to`: Agent or human user.
- `due_date`: Date.
- `cost_estimate`: Float (nullable).

## Context Objects (Nullable)
- `maintenance_context`: { `vendor_id`, `access_instructions`, `images_before`, `images_after` }.
- `finance_context`: { `invoice_amount`, `gl_account_code`, `payment_status` }.

## Audit And History (Immutable)
- `created_at`: ISO 8601 timestamp.
- `created_by`: String (user ID or agent ID).
- `last_updated_at`: ISO 8601 timestamp.
- `last_updated_by`: String.
- `interaction_log`: List of objects:
- `timestamp`: ISO 8601 timestamp.
- `actor`: "Intake Agent", "Gene Thompson", "Dan", etc.
- `action`: "Status Change", "Note Added", "Email Sent".
- `content`: The actual note or summary of the action.
