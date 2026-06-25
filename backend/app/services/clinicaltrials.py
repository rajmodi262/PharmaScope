"""ClinicalTrials.gov API v2 client — the live competitive-pipeline source.

Free, no API key. Docs: https://clinicaltrials.gov/data-api/api
We pull a normalised slice of fields and parse them into flat dicts the
synthesis layer can aggregate.
"""
from __future__ import annotations

from typing import List, Tuple
import httpx

BASE = "https://clinicaltrials.gov/api/v2/studies"

FIELDS = [
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.startDateStruct.date",
    "protocolSection.designModule.phases",
    "protocolSection.designModule.enrollmentInfo.count",
    "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
    "protocolSection.conditionsModule.conditions",
]

_PHASE_LABEL = {
    "EARLY_PHASE1": "Phase 1",
    "PHASE1": "Phase 1",
    "PHASE2": "Phase 2",
    "PHASE3": "Phase 3",
    "PHASE4": "Phase 4",
    "NA": "N/A",
}


def _phase(phases: List[str]) -> str:
    """Collapse a study's phase list to its highest (most advanced) phase."""
    order = ["PHASE4", "PHASE3", "PHASE2", "PHASE1", "EARLY_PHASE1", "NA"]
    for p in order:
        if p in (phases or []):
            return _PHASE_LABEL[p]
    return "N/A"


async def fetch(client: httpx.AsyncClient, query: str, page_size: int = 250) -> Tuple[List[dict], int]:
    """Return (trials, total_count). total_count is the full match count."""
    params = {
        "query.term": query,
        "fields": "|".join(FIELDS),
        "pageSize": str(min(page_size, 1000)),
        "countTotal": "true",
        "sort": "LastUpdatePostDate:desc",
    }
    r = await client.get(BASE, params=params, timeout=25)
    r.raise_for_status()
    data = r.json()
    total = int(data.get("totalCount", 0))

    trials: List[dict] = []
    for s in data.get("studies", []):
        ps = s.get("protocolSection", {})
        ident = ps.get("identificationModule", {})
        status = ps.get("statusModule", {})
        design = ps.get("designModule", {})
        spons = ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {})
        conds = ps.get("conditionsModule", {}).get("conditions", []) or []
        enroll = (design.get("enrollmentInfo") or {}).get("count")
        trials.append({
            "nct_id": ident.get("nctId", ""),
            "title": ident.get("briefTitle", "Untitled study"),
            "phase": _phase(design.get("phases", [])),
            "status": status.get("overallStatus", "UNKNOWN"),
            "sponsor": spons.get("name", "Unknown sponsor"),
            "enrollment": int(enroll) if isinstance(enroll, int) else None,
            "start_date": (status.get("startDateStruct") or {}).get("date"),
            "conditions": conds[:4],
        })
    return trials, total
