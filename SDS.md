# THE SOVEREIGN DEAL STATE (SDS)
# ------------------------------------------------------------------------------
# PHILOSOPHY:
# This file is the "Active Database" for a specific deal.
# Agents are FORBIDDEN from hallucinating data. They must strictly fill their
# assigned sections. If a field is unknown, it remains empty/zero/false and is
# treated as "null" by downstream logic.
# ------------------------------------------------------------------------------

## Field Ownership (Crosswalk)
- `master_status` -> The Manager
- `property_specs` -> The Scout
- `regulatory_table` -> The Planner
- `financials_table` -> The Underwriter
- `seller_profile` -> The Profiler
- `interaction_log` -> The Scribe
- `document_index` -> The Librarian
- `system_health` -> The Janitor

[master_status]
# Owner: THE MANAGER
# Function: The master status. The Manager watches this to route tasks.
deal_id = ""           # Unique Identifier
deal_stage = ""        # intake | underwriting | negotiation | closing | dead
priority_score = 0     # 1-100 (Calculated by Manager based on completeness)
active_blocker = ""    # The specific field stopping progress
last_updated = ""      # ISO-8601 timestamp

[property_specs]
# Owner: THE SCOUT
# Function: Raw physical data ingestion.
address = ""
county = ""
parcel_number = ""
lot_size_sqft = 0
existing_structure_sqft = 0
year_built = 0
current_condition = "unknown" # distress | turnkey | fixer
listing_source = ""           # off_market | mls | wholesaler

[regulatory_table]
# Owner: THE PLANNER
# Function: Regulatory constraints (zoning and feasibility).
zoning_code = ""              # e.g., "R-1", "CX", "IL"
overlay_districts = []        # e.g., ["historic", "transit"]
max_height_ft = 0
required_setbacks = { front = 0, side = 0, rear = 0 }
allowed_uses = []             # e.g., ["multifamily", "retail", "food_carts"]
adu_eligible = false

[financials_table]
# Owner: THE UNDERWRITER
# Function: Deterministic math. The Underwriter runs scripts to fill these.
# DO NOT VIBE CODE THESE NUMBERS.
purchase_price_ask = 0.0
strike_price_calculated = 0.0 # The max we will pay
arv_projected = 0.0           # After Repair Value
renovation_budget = 0.0
gross_potential_income = 0.0
noi_annual = 0.0
cap_rate_entry = 0.0
cash_on_cash_return = 0.0
financing_strategy = "cash"   # cash | seller_carry | subject_to | bank

[seller_profile]
# Owner: THE PROFILER
# Function: Qualitative leverage analysis.
seller_name = ""
motivation_level = "low"      # low | medium | high | desperate
pain_points = []              # e.g., ["probate", "taxes", "relocation"]
personality_type = ""         # analytical | emotional | assertive
negotiation_leverage = ""     # Summary of our angle

[interaction_log]
# Owner: THE SCRIBE (formerly Transcription Doctor)
# Function: Raw data processing.
last_contact_date = ""
contact_method = ""           # call | text | email | face_to_face
key_phrases_extracted = []    # Verbatim quotes indicating motivation
sentiment_score = 0.0         # -1.0 (hostile) to +1.0 (friendly)

[document_index]
# Owner: THE LIBRARIAN
# Function: File system mapping.
om_path = ""                  # Path to Offering Memorandum
photos_path = ""              # Path to property photos
county_records_path = ""
contract_draft_path = ""

[system_health]
# Owner: THE JANITOR
# Function: Metadata hygiene.
context_token_count = 0       # Monitors cost
file_integrity_check = true   # Do all paths in [document_index] exist?
archival_status = "active"    # active | cold_storage
