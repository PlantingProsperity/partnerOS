import requests
import json
import argparse
import os
import re
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- CONFIGURATION ---
GEOCODE_URL = "https://gis.clark.wa.gov/arcgisfedpw/rest/services/Geocoders/SitusStreetsParks/GeocodeServer/findAddressCandidates"
PARCEL_URL = "https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/TaxlotsPublic/MapServer/0/query"
QUIET = os.getenv("PINNEO_QUIET") == "1"

def log(message):
    if not QUIET:
        print(message)

def slugify(text):
    """Turns '123 Main St' into '123-main-st'"""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def get_robust_session():
    """
    Creates a requests session that auto-retries on flakes/timeouts.
    Retries 3 times with exponential backoff (0.5s, 1s, 2s).
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_clark_county_data(address):
    log(f"🔍 [Scout] Searching Clark County GIS for: {address}...")
    session = get_robust_session()
    
    # 1. Geocode
    try:
        r = session.get(GEOCODE_URL, params={
            "SingleLine": address, "outFields": "*", "maxLocations": 1, "f": "pjson"
        }, timeout=10)
        data = r.json()
        
        if not data.get("candidates"):
            log("❌ [Scout] Address not found.")
            return None
            
        loc = data["candidates"][0]["location"]
        log(f"📍 [Scout] Found coordinates: {loc['x']}, {loc['y']}")

        # 2. Parcel Query
        r = session.get(PARCEL_URL, params={
            "geometry": json.dumps(loc),
            "geometryType": "esriGeometryPoint",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "Prop_id,SitusAddrsFull,GISSqft,BldgYrBlt,Zone1,AssrSqFt,MktLandVal,MktBldgVal",
            "f": "pjson"
        }, timeout=10)
        p_data = r.json()

        if not p_data.get("features"):
            log("⚠️ [Scout] No parcel found at location.")
            return None

        attrs = p_data["features"][0]["attributes"]
        
        # 3. Map to Internal Schema Keys
        return {
            "property_address": attrs.get("SitusAddrsFull") or address,
            "parcel_id": attrs.get("Prop_id"),
            "valuation": {
                "assessed_value": (attrs.get("MktLandVal") or 0) + (attrs.get("MktBldgVal") or 0),
                "tax_assessed_year": datetime.now().year - 1
            },
            "zoning": {
                "zoning_code": attrs.get("Zone1"),
                "lot_size_sf": attrs.get("GISSqft"),
                "year_built": attrs.get("BldgYrBlt"),
                "building_sqft": attrs.get("AssrSqFt"),
                "development_potential": None
            },
            "meta": {
                "scout_source": "Clark County GIS",
                "scout_timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        log(f"❌ [Scout] Error: {e}")
        return None

def save_deal_state(data):
    """Creates the folder structure and saves the Analysis JSON"""
    if not data:
        return

    # Create Deal Folder
    property_address = data.get("property_address") or "unknown-address"
    slug = slugify(property_address)
    deal_path = f"deals/active/{slug}"
    os.makedirs(deal_path, exist_ok=True)

    # Load existing or create new Analysis Schema structure
    schema_path = f"{deal_path}/analysis.json"
    
    # Base structure based on ANALYSIS_SCHEMA.md
    analysis_state = {
        "address": property_address,
        "status": "New_Lead",
        "valuation": data["valuation"],
        "project_costs": {},
        "investment_metrics": {},
        "zoning": data["zoning"],
        "meta": data.get("meta", {})
    }

    with open(schema_path, "w") as f:
        json.dump(analysis_state, f, indent=2)
    
    log(f"💾 [Scout] Deal initialized at: {schema_path}")
    return schema_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="Target Property Address")
    args = parser.parse_args()

    data = fetch_clark_county_data(args.address)
    save_deal_state(data)
