"""Synthesis layer — aggregate raw trials + regulatory data into the analyst view.

This is the analytical core: it turns hundreds of raw trial records into a
competitive pipeline, a sponsor leaderboard, a momentum timeline, and a
rule-based **Insights / Opportunities / Threats** brief. No LLM required, so it
is fully deterministic and demo-safe; an LLM can later enrich the narrative.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

PHASES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
ACTIVE = {"RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING", "NOT_YET_RECRUITING"}


def _pct(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def _year(date: Optional[str]) -> Optional[int]:
    if not date:
        return None
    try:
        return int(date[:4])
    except (ValueError, TypeError):
        return None


def build(query: str, resolved_type: str, trials: List[dict], total: int,
          regulatory: Optional[dict], safety: List[dict],
          sources: List[str], cached: bool, degraded: bool) -> dict:
    n = len(trials)

    # ---- pipeline funnel
    phase_counts = Counter(t["phase"] for t in trials)
    pipeline = [{"phase": p, "count": phase_counts.get(p, 0)} for p in PHASES]
    late_stage = phase_counts.get("Phase 3", 0) + phase_counts.get("Phase 4", 0)

    # ---- sponsor leaderboard
    sponsor_counts = Counter(t["sponsor"] for t in trials if t["sponsor"])
    sponsors = [{"name": name, "trials": c, "share": _pct(c, n)}
                for name, c in sponsor_counts.most_common(8)]

    # ---- status mix
    status_counts = Counter(t["status"] for t in trials)
    status_mix = [{"status": s.replace("_", " ").title(), "count": c}
                  for s, c in status_counts.most_common(6)]
    active = sum(c for s, c in status_counts.items() if s in ACTIVE)

    # ---- momentum timeline (last ~12 yrs)
    years = Counter(y for t in trials if (y := _year(t.get("start_date"))) and y >= 2005)
    timeline = [{"year": y, "starts": years.get(y, 0)}
                for y in range(min(years) if years else 2015,
                               (max(years) if years else 2024) + 1)]

    regulatory = regulatory or {"approved": False, "brand_names": [], "manufacturers": [],
                                "routes": [], "indication": None}

    brief = _brief(query, resolved_type, n, total, pipeline, sponsors, late_stage,
                   active, regulatory, safety)

    return {
        "summary": {
            "total_trials": total,
            "tracked_trials": n,
            "active_trials": active,
            "late_stage_trials": late_stage,
            "sponsor_count": len(sponsor_counts),
            "approved": regulatory["approved"],
        },
        "pipeline": pipeline,
        "sponsors": sponsors,
        "timeline": timeline,
        "status_mix": status_mix,
        "regulatory": regulatory,
        "safety": safety,
        "trials": trials[:60],
        "brief": brief,
        "meta": {
            "query": query,
            "resolved_type": resolved_type,
            "sources": sources,
            "cached": cached,
            "degraded": degraded,
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        },
    }


def _brief(query, rtype, n, total, pipeline, sponsors, late_stage, active,
           regulatory, safety) -> dict:
    insights, opps, threats = [], [], []
    q = query.title()
    pc = {p["phase"]: p["count"] for p in pipeline}

    insights.append(
        f"**{total:,}** registered trials reference **{q}**; this analysis profiles the "
        f"**{n}** most recently updated. **{active}** are actively enrolling or running.")

    if late_stage:
        insights.append(
            f"**{late_stage}** late-stage (Phase 3/4) programmes are in play — a "
            f"{'mature, competitive' if late_stage > 8 else 'developing'} commercial landscape.")
    if pc.get("Phase 1", 0) or pc.get("Phase 2", 0):
        insights.append(
            f"Early pipeline depth: **{pc.get('Phase 1',0)}** Phase 1 and "
            f"**{pc.get('Phase 2',0)}** Phase 2 studies signal sustained future entry.")

    if sponsors:
        top = sponsors[0]
        insights.append(
            f"**{top['name']}** leads activity with **{top['trials']}** trials "
            f"(**{top['share']}%** of tracked studies).")
        if len(sponsors) >= 3:
            threats.append(
                f"Concentrated competition: top-3 sponsors "
                f"({', '.join(s['name'] for s in sponsors[:3])}) drive "
                f"**{round(sum(s['share'] for s in sponsors[:3]),1)}%** of activity.")

    if regulatory.get("approved"):
        brands = ", ".join(regulatory.get("brand_names", [])[:3]) or "approved products"
        insights.append(
            f"FDA-labelled and on-market as **{brands}** "
            f"({', '.join(regulatory.get('manufacturers', [])[:2]) or 'n/a'}).")
        threats.append(
            "Branded incumbents already hold the indication — new entrants must "
            "differentiate on efficacy, safety, or access to win share.")
    else:
        opps.append(
            f"No FDA-approved label matched **{q}** in openFDA — a potential "
            f"**white-space / pre-approval** opportunity if late-stage assets read out positively.")

    if late_stage <= 3 and (pc.get("Phase 1", 0) + pc.get("Phase 2", 0)) >= 5:
        opps.append(
            "Pipeline skews early-stage: a **fast-follower or in-licensing** play could "
            "reach the market alongside the first wave of approvals.")
    if active >= 10:
        opps.append(
            f"**{active}** active trials indicate strong investigator and patient interest — "
            f"favourable conditions for recruitment, partnering, and KOL engagement.")

    if safety:
        top_ae = ", ".join(f"{s['reaction']} ({s['count']:,})" for s in safety[:3])
        threats.append(
            f"Dominant real-world adverse-event signals (FAERS): **{top_ae}** — "
            f"tolerability messaging and risk management will shape uptake.")

    if not opps:
        opps.append("Monitor late-stage readouts and label expansions for share-shift windows.")
    if not threats:
        threats.append("Competitive intensity is currently low — first-mover advantage is defensible.")
    return {"insights": insights, "opportunities": opps, "threats": threats}
