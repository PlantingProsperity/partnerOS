"""Scout market-intelligence retrieval helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlparse

import requests

from partner_os.constants import HIGH_CONFIDENCE_DOMAINS, MEDIUM_CONFIDENCE_DOMAINS
from partner_os.models import ScoutClaim


@dataclass(slots=True)
class WebSearchClient:
    timeout_seconds: int = 15

    def search(self, query: str, limit: int = 6) -> list[ScoutClaim]:
        """Fetch web results using DuckDuckGo HTML endpoint."""
        response = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        html = response.text

        claims: list[ScoutClaim] = []
        pattern = re.compile(
            r'<a rel="nofollow" class="result__a" href="(?P<url>.*?)">(?P<title>.*?)</a>.*?'
            r'<a class="result__snippet".*?>(?P<snippet>.*?)</a>',
            re.DOTALL,
        )

        for match in pattern.finditer(html):
            url = unescape(match.group("url"))
            title = re.sub(r"<.*?>", "", unescape(match.group("title"))).strip()
            snippet = re.sub(r"<.*?>", "", unescape(match.group("snippet"))).strip()
            label, score = classify_confidence(url)
            claims.append(
                ScoutClaim(
                    title=title,
                    url=url,
                    summary=snippet,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    confidence_label=label,
                    confidence_score=score,
                )
            )
            if len(claims) >= limit:
                break

        return claims



def classify_confidence(url: str) -> tuple[str, int]:
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    if any(domain.endswith(item) for item in HIGH_CONFIDENCE_DOMAINS):
        return ("High", 90)
    if any(domain.endswith(item) for item in MEDIUM_CONFIDENCE_DOMAINS):
        return ("Medium", 70)
    return ("Low", 40)
