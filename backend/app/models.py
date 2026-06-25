"""Typed response contract for the Pharma Intelligence API.

Every field the frontend consumes is declared here so the React client can be
generated/typed against a single source of truth.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Trial(BaseModel):
    nct_id: str
    title: str
    phase: str                       # "Phase 1".."Phase 4" | "N/A"
    status: str                      # RECRUITING | COMPLETED | ...
    sponsor: str
    enrollment: Optional[int] = None
    start_date: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)


class PhaseBucket(BaseModel):
    phase: str
    count: int


class SponsorShare(BaseModel):
    name: str
    trials: int
    share: float                     # % of tracked trials


class TimelinePoint(BaseModel):
    year: int
    starts: int


class StatusBucket(BaseModel):
    status: str
    count: int


class Regulatory(BaseModel):
    approved: bool = False
    brand_names: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
    routes: List[str] = Field(default_factory=list)
    indication: Optional[str] = None


class SafetySignal(BaseModel):
    reaction: str
    count: int


class Brief(BaseModel):
    insights: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)


class Summary(BaseModel):
    total_trials: int
    tracked_trials: int
    active_trials: int
    late_stage_trials: int           # Phase 3 + 4
    sponsor_count: int
    approved: bool


class Meta(BaseModel):
    query: str
    resolved_type: Literal["drug", "indication"]
    sources: List[str]
    cached: bool
    degraded: bool = False           # served from fallback after a live failure
    fetched_at: str


class Intelligence(BaseModel):
    summary: Summary
    pipeline: List[PhaseBucket]
    sponsors: List[SponsorShare]
    timeline: List[TimelinePoint]
    status_mix: List[StatusBucket]
    regulatory: Regulatory
    safety: List[SafetySignal]
    trials: List[Trial]
    brief: Brief
    meta: Meta
