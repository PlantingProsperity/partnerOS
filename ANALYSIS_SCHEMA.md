# Analysis Schema (Pre-Offer Investment Underwriting)

## Goal
Capture investment underwriting using the Pinneo method. This separates price from terms and determines viability before any offer is drafted.

## Required Fields (Grouped)

### Valuation And Market Data
- `arv` (After Repair Value): Float.
- `as_is_value`: Float (current condition).
- `comps_summary`: String or link to CMA.
- `rent_roll_current`: Monthly total.
- `rent_roll_pro_forma`: Monthly total (market rents).

### Project Costs (Rehab Or Flip Math)
- `rehab_budget`: Float (estimated).
- `contingency_percent`: Float (default 10%).
- `holding_costs`: Monthly (taxes, insurance, utilities, debt service).
- `timeline_months`: Integer (flip duration or stabilization period).

### Investment Metrics (Pinneo Lens)
- `cap_rate`: Float (NOI / Purchase Price).
- `cash_on_cash`: Float (cash flow / cash invested).
- `mao_flip`: Maximum allowable offer for a flip (ARV * 70% - Rehab).
- `mao_hold`: Maximum allowable offer for a rental (based on min cash flow).
- `exit_strategy`: Enum [Flip, BRRRR, Long_Term_Hold, Wholesale, Wholetail].

### Creative Finance Toggles
- `seller_financing_terms`: Object { rate, down, term, balloon }.
- `subject_to_capacity`: Boolean (existing debt assumable or sub-to compatible).
- `partner_equity_split`: Percent (if using OPM).

### Decision Output
- `status`: Enum [Draft, Under_Review, Approved_for_Offer, Rejected, Archived].
- `target_offer_price`: Float.
- `max_offer_price`: Float.
- `notes`: String (risk factors, "hair on the deal").

### Development And Zoning (Optional)
- `zoning_code`: String (e.g., "R-1", "CX", "IL").
- `lot_size_sf`: Float.
- `setbacks`: Object { front, side, rear }.
- `overlays`: List (e.g., "Transit", "Historic", "Critical Areas").
- `highest_best_use`: String (e.g., "Mixed Use", "Multifamily", "Food Cart Pod").
- `development_potential`: Boolean.
