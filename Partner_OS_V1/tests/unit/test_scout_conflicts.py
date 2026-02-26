from __future__ import annotations

from partner_os.agents.scout import ScoutAgent
from partner_os.config import load_config
from partner_os.db.store import DataStore
from partner_os.models import ScoutClaim
from partner_os.services.search import WebSearchClient, classify_confidence


class DummySearch(WebSearchClient):
    def search(self, query: str, limit: int = 6):  # noqa: ARG002
        return []


def test_confidence_classification():
    high = classify_confidence("https://www.clark.wa.gov/something")
    medium = classify_confidence("https://www.costar.com/news")
    low = classify_confidence("https://randomblog.example/post")

    assert high[0] == "High"
    assert medium[0] == "Medium"
    assert low[0] == "Low"


def test_market_conflict_detection(tmp_path):
    config = load_config(root_override=tmp_path)
    store = DataStore(config.database_path)
    scout = ScoutAgent(name="Scout", config=config, store=store, search_client=DummySearch())

    claims = [
        ScoutClaim(
            title="Cap Rate Report A",
            url="https://example.com/a",
            summary="Clark County cap rate now 5.0% for multifamily.",
            timestamp_utc="2026-02-26T00:00:00Z",
            confidence_label="Low",
            confidence_score=40,
        ),
        ScoutClaim(
            title="Cap Rate Report B",
            url="https://example.com/b",
            summary="Analyst says cap rate close to 6.2% this quarter.",
            timestamp_utc="2026-02-26T00:00:01Z",
            confidence_label="Low",
            confidence_score=40,
        ),
    ]

    conflicts = scout._detect_market_conflicts(claims)
    assert conflicts

    store.close()
