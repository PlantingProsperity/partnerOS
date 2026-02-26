import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["PINNEO_QUIET"] = "1"

import scripts.scout_scrape as ss


class TestScoutScrape(unittest.TestCase):
    def test_slugify_basic(self):
        self.assertEqual(ss.slugify("123 Main St"), "123-main-st")

    def test_fetch_clark_county_data_parses_response(self):
        class DummyResp:
            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        class DummySession:
            def __init__(self):
                self.calls = []

            def get(self, url, params=None, timeout=10):
                self.calls.append((url, params))
                if url == ss.GEOCODE_URL:
                    return DummyResp({
                        "candidates": [{"location": {"x": 1, "y": 2}}]
                    })
                return DummyResp({
                    "features": [{"attributes": {
                        "SitusAddrsFull": "1 Main St",
                        "Prop_id": "P1",
                        "GISSqft": 1000,
                        "BldgYrBlt": 1990,
                        "Zone1": "R1",
                        "AssrSqFt": 800,
                        "MktLandVal": 100000,
                        "MktBldgVal": 150000,
                    }}]
                })

        with patch.object(ss, "get_robust_session", return_value=DummySession()):
            data = ss.fetch_clark_county_data("1 Main St")

        self.assertEqual(data["property_address"], "1 Main St")
        self.assertEqual(data["parcel_id"], "P1")
        self.assertEqual(data["valuation"]["assessed_value"], 250000)
        self.assertEqual(data["zoning"]["zoning_code"], "R1")

    def test_save_deal_state_writes_analysis_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                data = {
                    "property_address": "1 Main St",
                    "valuation": {"assessed_value": 250000, "tax_assessed_year": 2025},
                    "zoning": {
                        "zoning_code": "R1",
                        "lot_size_sf": 1000,
                        "year_built": 1990,
                        "building_sqft": 800,
                        "development_potential": None,
                    },
                    "meta": {"scout_source": "X", "scout_timestamp": "t"},
                }
                path = ss.save_deal_state(data)
                self.assertIsNotNone(path)
                path = Path(path)
                self.assertTrue(path.exists())
                payload = json.loads(path.read_text())
                self.assertEqual(payload["address"], "1 Main St")
                self.assertEqual(payload["valuation"]["assessed_value"], 250000)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
