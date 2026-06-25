"""openFDA client — regulatory status, labelling, and safety-signal source.

Free, no API key (rate-limited). Docs: https://open.fda.gov/apis/
Two calls: drug *label* (approval + indication) and adverse-*event* counts.
Both fail soft — openFDA returns HTTP 404 when a search has no matches.
"""
from __future__ import annotations

from typing import List, Optional
import httpx

LABEL = "https://api.fda.gov/drug/label.json"
EVENT = "https://api.fda.gov/drug/event.json"


def _dedupe(items) -> List[str]:
    seen, out = set(), []
    for x in items or []:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


async def fetch_label(client: httpx.AsyncClient, query: str) -> Optional[dict]:
    """Try generic_name then brand_name. Return None if nothing matches."""
    for field in ("openfda.generic_name", "openfda.brand_name", "openfda.substance_name"):
        try:
            r = await client.get(
                LABEL, params={"search": f'{field}:"{query}"', "limit": "1"}, timeout=20)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            results = r.json().get("results", [])
            if not results:
                continue
            res = results[0]
            of = res.get("openfda", {})
            indic = res.get("indications_and_usage", [])
            indication = indic[0].strip()[:420] if indic else None
            return {
                "approved": True,
                "brand_names": _dedupe(of.get("brand_name"))[:6],
                "manufacturers": _dedupe(of.get("manufacturer_name"))[:4],
                "routes": _dedupe(of.get("route"))[:4],
                "indication": indication,
            }
        except (httpx.HTTPError, ValueError):
            continue
    return None


async def fetch_safety(client: httpx.AsyncClient, query: str, limit: int = 8) -> List[dict]:
    """Top adverse reactions reported for the drug (FAERS aggregate counts)."""
    try:
        r = await client.get(EVENT, params={
            "search": f'patient.drug.openfda.generic_name:"{query}"',
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": str(limit),
        }, timeout=20)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return [{"reaction": x["term"].title(), "count": int(x["count"])}
                for x in r.json().get("results", [])]
    except (httpx.HTTPError, ValueError, KeyError):
        return []
