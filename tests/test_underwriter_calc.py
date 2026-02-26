import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ["PINNEO_QUIET"] = "1"

import scripts.underwriter_calc as uc


class TestUnderwriterCalc(unittest.TestCase):
    def test_normalize_schema_backfills_assessed_and_zoning(self):
        data = {
            "valuation": {"assessed_value": 123},
            "zoning": {"zoning_code": "R1", "lot_size_sf": 1000, "development_potential": True},
        }
        norm = uc.normalize_schema(data)
        self.assertEqual(norm["as_is_value"], 123)
        self.assertEqual(norm["zoning_code"], "R1")
        self.assertEqual(norm["lot_size_sf"], 1000)
        self.assertTrue(norm["development_potential"])

    def test_generate_markdown_report_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_path = Path(tmp_dir) / "analysis.json"
            analysis_path.write_text("{}")
            data = {
                "address": "1 Main St",
                "valuation": {"arv": 300000},
                "project_costs": {"rehab_budget": 50000},
                "investment_metrics": {"mao_flip": 100000, "buy_box_target": 90000, "exit_strategy": "Flip"},
                "zoning": {"zoning_code": "R1", "year_built": 1990, "lot_size_sf": 1000, "building_sqft": 800, "development_potential": None},
                "meta": {"scout_source": "X"},
            }
            uc.generate_markdown_report(data, str(analysis_path))
            report = Path(tmp_dir) / "analysis_report.md"
            self.assertTrue(report.exists())
            text = report.read_text()
            self.assertIn("Deal Analysis", text)

    def test_load_deal_finds_partial_slug(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir) / "deals" / "active" / "123-main-st"
            base.mkdir(parents=True)
            analysis = base / "analysis.json"
            analysis.write_text(json.dumps({"address": "1 Main St"}))

            cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                data, path = uc.load_deal("main")
                self.assertEqual(data["address"], "1 Main St")
                self.assertEqual(Path(path), Path("deals/active/123-main-st/analysis.json"))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
