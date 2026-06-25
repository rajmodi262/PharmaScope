"""Pharma Intelligence API — FastAPI gateway.

One hero endpoint, ``GET /api/intelligence``, orchestrates concurrent live calls
to ClinicalTrials.gov and openFDA, synthesises an analyst view, and returns a
single typed payload. Resilience: 12h disk cache + stale-fallback so a flaky
upstream never yields an empty screen.
"""
from __future__ import annotations

import asyncio

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .cache import read as cache_read, write as cache_write
from .models import Intelligence
from .services import clinicaltrials, openfda, synthesis

app = FastAPI(
    title="EconoScope · Pharma Intelligence API",
    version="2.0.0",
    description="Live biopharma pipeline & competitive intelligence over "
                "ClinicalTrials.gov and openFDA.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

INDICATION_HINTS = (
    "cancer", "obesity", "diabetes", "asthma", "alzheimer", "depression",
    "arthritis", "covid", "migraine", "psoriasis", "hypertension", "disease",
    "syndrome", "disorder", "fibrosis", "leukemia", "lymphoma", "carcinoma",
)


def _classify(q: str) -> str:
    ql = q.lower()
    return "indication" if any(h in ql for h in INDICATION_HINTS) else "drug"


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pharma-intelligence", "version": "2.0.0"}


@app.get("/api/intelligence", response_model=Intelligence)
async def intelligence(
    q: str = Query(..., min_length=2, description="Drug name or indication"),
    refresh: bool = Query(False, description="Bypass cache and force a live fetch"),
):
    q = q.strip()
    resolved_type = _classify(q)
    cache_key = f"intel::{q.lower()}"

    if not refresh:
        fresh = cache_read(cache_key)
        if fresh:
            fresh["meta"]["cached"] = True
            return fresh

    sources, degraded = [], False
    trials, total, regulatory, safety = [], 0, None, []

    try:
        async with httpx.AsyncClient(headers={"User-Agent": "EconoScope/2.0"}) as client:
            ct_task = clinicaltrials.fetch(client, q)
            label_task = openfda.fetch_label(client, q)
            safety_task = openfda.fetch_safety(client, q)
            (trials, total), regulatory, safety = await asyncio.gather(
                ct_task, label_task, safety_task)
        sources = ["ClinicalTrials.gov API v2", "openFDA (label + FAERS)"]
    except Exception:
        # Graceful degradation: serve last good payload regardless of age.
        stale = cache_read(cache_key, allow_stale=True)
        if stale:
            stale["meta"]["cached"] = True
            stale["meta"]["degraded"] = True
            return stale
        degraded = True
        sources = ["unavailable — upstream APIs unreachable"]

    payload = synthesis.build(
        query=q, resolved_type=resolved_type, trials=trials, total=total,
        regulatory=regulatory, safety=safety, sources=sources,
        cached=False, degraded=degraded)

    if trials:
        cache_write(cache_key, payload)
    return payload
