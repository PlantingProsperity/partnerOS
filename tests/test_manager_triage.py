import os
import unittest
from unittest.mock import patch

os.environ["PINNEO_QUIET"] = "1"

import scripts.manager_triage as mt


class TestManagerTriage(unittest.TestCase):
    def test_clean_json_output_strips_markdown_wrappers(self):
        raw = """```json\n{\"a\": 1}\n```"""
        cleaned = mt.clean_json_output(raw)
        self.assertEqual(cleaned, '{"a": 1}')

    def test_slugify_basic(self):
        self.assertEqual(
            mt.slugify("123 Main St, Portland, OR"),
            "123-main-st-portland-or",
        )

    def test_parse_lead_with_gemini_parses_json(self):
        with patch.object(mt, "call_gemini_api") as mock_call:
            mock_call.return_value = '{"address": "1 Main St", "seller_name": "A", "phone": "1", "email": "e", "motivation_score": 5, "story": "s", "tags": ["t"]}'
            data = mt.parse_lead_with_gemini("x.txt", "raw")
        self.assertEqual(data["address"], "1 Main St")

    def test_parse_lead_with_gemini_bad_json_returns_none(self):
        with patch.object(mt, "call_gemini_api", return_value="not-json"):
            self.assertIsNone(mt.parse_lead_with_gemini("x.txt", "raw"))


if __name__ == "__main__":
    unittest.main()
