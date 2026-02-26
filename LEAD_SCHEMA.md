# Lead Schema (Pre-Analysis Intake)

## Goal
Track raw intake and relationship nurturing before any property analysis happens.

## Status Lifecycle
New -> Attempted Contact -> Connected -> Nurture (Long term) -> Qualified (Ready for Analysis) -> Dead/Archived

## Required Fields (Grouped)

### Identity
- `lead_id`
- `created_at`
- `source` (e.g., "Sign Call", "Driving for Dollars", "Referral", "Website")
- `marketing_consent`: Boolean.
- `do_not_contact`: Boolean.

### Contact
- `name`
- `phone`
- `email`
- `role` (Seller, Wholesaler, Bird Dog)

### Property Context (Optional)
- `address`
- `parcel_id`

### The Story (Pinneo Method)
- `motivation_level` (1-10)
- `pain_points` (String)
- `timeline` (String)

### Ops
- `status` (Enum)
- `assigned_agent` (User)
- `last_contact_date`
- `next_followup_date`
- `interaction_log` (List of notes)
