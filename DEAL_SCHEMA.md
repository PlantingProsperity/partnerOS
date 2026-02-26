# Deal Schema (Washington Investment Brokerage)

This section defines the strict Deal Schema used as the single source of truth. A Deal is instantiated only when the decision is made to draft an offer. Leads and Analysis are separate upstream objects and must reference the Deal once created.

## Deal Stages And Triggers
1. Drafting/Structuring
- Trigger: Decision to make an offer (promoted from Analysis).
- Focus: Defining creative terms, drafting the PSA (Form 21), aligning internal partners.

2. Negotiation
- Trigger: Sending the signed Offer (PSA) to the Seller or Listing Agent.
- Focus: Counter-offers, price adjustments, term refinement.

3. Mutual Acceptance (The Clock Starts)
- Trigger: PSA fully signed and dated by both parties.
- Focus: Strictly tracking the timeline (Day 0).

4. Feasibility/Due Diligence
- Trigger: Receipt of Earnest Money (Form 31) or opening of Escrow.
- Focus: Inspections (Form 35), Title Review (Form 22T), Seller Disclosure (Form 17).

5. Funding/Partner Alignment (Investor Specific)
- Trigger: Inspection Contingency Waived or Satisfied (Form 35R).
- Focus: Finalizing private money, hard money, or partnership funds.

6. Escrow/Closing Prep
- Trigger: Funding committed or Loan Docs ordered.
- Focus: Signing, HUD/CD review, final walkthrough.

7. Closed
- Trigger: Recording Numbers received from the County.
- Focus: Commission disbursement, file compliance audit.

8. Post-Close/Asset Mgmt
- Trigger: Possession or Keys received.
- Focus: Handover to rehab crew or property management.

## Critical Deadlines To Track
- Earnest Money Deposit (default: mutual acceptance + 2 days).
- Seller Disclosure Review (default: mutual acceptance + 3 days).
- Inspection Response (default: mutual acceptance + 10 days).
- Title Review (default: receipt + 5 days).
- Financing Contingency (Form 22A deadline).
- Hard Money or Private Capital Commitment Date (custom investor deadline).

## Required Fields (Grouped)

### Property Identity
- `property_address`: Full street address, City, State, Zip.
- `parcel_number`: Tax Parcel ID.
- `legal_description`: Abbreviated legal.
- `mls_number`: NWMLS Listing ID (if on-market).

### Parties (The Rolodex)
- `buyer_entity`: Purchasing entity (individual, LLC, or "and/or assigns").
- `seller_name`: Legal owner name(s).
- `listing_agent`: Name, Firm, Email, Phone, License #.
- `escrow_officer`: Name, Company, Email, Team Phone.
- `title_officer`: Name, Company, Email.
- `lender_contact`: Name, Email (private, hard money, or conventional).

### Financials And Terms
- `purchase_price`: Float.
- `earnest_money`: Amount, Form (Check/Wire/Note), Holder (Closing Agent or Firm).
- `financing_type`: Enum [Cash, Conventional, FHA/VA, Seller Carry, Subject-To, Hard Money].
- `creative_terms`: Object { down_payment, interest_rate, amortization, balloon_date, monthly_payment } (nullable).
- `commission_split`: % to Selling Office, % to Listing Office.

### The Clock (Critical Dates)
- `mutual_acceptance_date`: Date.
- `closing_date`: Date.
- `possession_date`: Date (e.g., "Closing", "Closing + 3 Days").

### Contingencies And Deadlines (Computed From Mutual Acceptance)
- `earnest_money_due`: Date (default: mutual acceptance + 2 days).
- `seller_disclosure_review`: Date (default: mutual acceptance + 3 days).
- `inspection_period_end`: Date (default: mutual acceptance + 10 days).
- `title_review_end`: Date (default: receipt + 5 days).
- `financing_contingency_end`: Date (Form 22A deadline).

### Documents And Compliance
- `transaction_id`: Internal Firm ID.
- `required_docs`: Enum list [PSA_21, Form_17, Form_35, Form_22A, Law_Pamphlet, Agency_Pamphlet].
- `doc_status`: Map of document to status [Missing, Drafted, Signed, Uploaded].

### Compliance And Agency (Weichert Standards)
- `agency_disclosure_date`: Date Form 42 (Agency Disclosure) was signed.
- `pamphlet_receipt_date`: Date "Law of Real Estate Agency" pamphlet was sent or acknowledged.
- `firm_license_info`: Object { name: "Weichert, Realtors - Equity NW", license_number: [auto-filled], address: [auto-filled] }.
- `principal_broker_review`: Boolean (has Gene reviewed or initialed).
- `commission_disbursement_form`: Status [Not Started, Submitted, Approved].
- `referral_agreement`: Object { agent_name, firm, percent_split } (nullable).
- `lead_source`: String (tracked for ROI reporting).
- `investor_partner_entity`: String (if a partner is involved in funding or equity).

### Audit And System Meta (Immutable)
- `created_by`: String (user ID or agent ID).
- `created_at`: ISO 8601 timestamp.
- `last_updated_by`: String.
- `last_updated_at`: ISO 8601 timestamp.
- `update_reason`: String (required for manual overrides).
- `change_log`: List of objects { timestamp, actor, field, old_val, new_val }.

### Validation And Defaults

Defaults (Computed)
- `earnest_money_due` = `mutual_acceptance_date` + 2 business days.
- `seller_disclosure_review` = `mutual_acceptance_date` + 3 business days.
- `inspection_period_end` = `mutual_acceptance_date` + 10 calendar days.
- `title_review_end` = `title_receipt_date` + 5 business days.
- `possession_date` defaults to `closing_date` unless overridden.

Validation Rules
- `deal_id`: Required and unique (UUID or internal slug).
- `mutual_acceptance_date`: Required if status is active, pending, or closed.
- `purchase_price`: Must be > 0.
- `earnest_money`: Must be > 0.
- `status`: Must match defined enum values.
- `required_docs`: At least PSA_21 required to enter Stage 2 (Negotiation).
