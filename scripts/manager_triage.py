import os
import json
import subprocess
import shutil
import re
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- CONFIGURATION ---
load_dotenv()
INBOX_DIR = "leads/inbox"
ARCHIVE_DIR = "leads/archive"
ACTIVE_DIR = "leads/active"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
QUIET = os.getenv("PINNEO_QUIET") == "1"

def log(message):
    if not QUIET:
        print(message)

def clean_json_output(text):
    """Strips markdown wrappers from AI response."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()

def get_robust_session():
    """
    Creates a requests session with retries for 429/5xx.
    Respects Retry-After header when present.
    """
    session = requests.Session()
    retry = Retry(
        total=4,
        read=4,
        connect=4,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def call_gemini_api(prompt):
    """Calls Gemini API via HTTP (Headless/No CLI required)."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"},
    }

    try:
        session = get_robust_session()
        response = session.post(GEMINI_URL, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        log(f"❌ [Manager] API Error: {e}")
        return None

def parse_lead_with_gemini(filename, text):
    log(f"🧠 [Manager] Analyzing {filename}...")

    prompt = f"""
    You are 'The Manager'. Extract these fields from the text into JSON:
    {{
      "address": "Full Street Address, City, State, Zip",
      "seller_name": "Name",
      "phone": "Phone",
      "email": "Email",
      "motivation_score": 1-10,
      "story": "Summary",
      "tags": ["tag1", "tag2"]
    }}
    RAW TEXT:
    {text}
    """

    response_text = call_gemini_api(prompt)
    if not response_text:
        return None

    try:
        cleaned = clean_json_output(response_text)
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError:
        log("❌ [Manager] Failed to decode JSON from AI response.")
        return None

def slugify(text):
    if not text:
        return "unknown-lead"
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def process_inbox():
    if not GEMINI_API_KEY:
        log("⛔ [Manager] FATAL: GEMINI_API_KEY not found in .env or environment.")
        sys.exit(1)

    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(ACTIVE_DIR, exist_ok=True)

    files = [f for f in os.listdir(INBOX_DIR) if f.endswith(".txt")]

    if not files:
        log("📭 [Manager] Inbox empty.")
        return

    log(f"📨 [Manager] Found {len(files)} new lead(s). Processing...")

    for filename in files:
        filepath = os.path.join(INBOX_DIR, filename)

        with open(filepath, "r") as f:
            raw_text = f.read()

        lead_data = parse_lead_with_gemini(filename, raw_text)

        if not lead_data or not lead_data.get("address"):
            log(f"⚠️ [Manager] Failed to extract address. LEAVING in Inbox.")
            continue

        slug = slugify(lead_data["address"])
        deal_path = os.path.join(ACTIVE_DIR, slug)
        os.makedirs(deal_path, exist_ok=True)

        lead_json_path = os.path.join(deal_path, "lead.json")
        with open(lead_json_path, "w") as f:
            json.dump(lead_data, f, indent=2)

        log(f"✅ [Manager] Created Deal: {slug}")

        log("   🚀 Triggering Scout...")
        try:
            subprocess.run(["python", "scripts/scout_scrape.py", lead_data["address"]], check=True)
        except subprocess.CalledProcessError:
            log("   ⚠️ Scout failed (Network/Data issue). Deal created but not enriched.")

        shutil.move(filepath, os.path.join(ARCHIVE_DIR, filename))
        log(f"   🗄️  Archived {filename}")

if __name__ == "__main__":
    process_inbox()
