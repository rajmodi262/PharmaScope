// Typed client for the Pharma Intelligence API. Mirrors backend/app/models.py.

export interface Trial {
  nct_id: string;
  title: string;
  phase: string;
  status: string;
  sponsor: string;
  enrollment: number | null;
  start_date: string | null;
  conditions: string[];
}

export interface PhaseBucket { phase: string; count: number; }
export interface SponsorShare { name: string; trials: number; share: number; }
export interface TimelinePoint { year: number; starts: number; }
export interface StatusBucket { status: string; count: number; }
export interface SafetySignal { reaction: string; count: number; }

export interface Regulatory {
  approved: boolean;
  brand_names: string[];
  manufacturers: string[];
  routes: string[];
  indication: string | null;
}

export interface Brief {
  insights: string[];
  opportunities: string[];
  threats: string[];
}

export interface Summary {
  total_trials: number;
  tracked_trials: number;
  active_trials: number;
  late_stage_trials: number;
  sponsor_count: number;
  approved: boolean;
}

export interface Meta {
  query: string;
  resolved_type: "drug" | "indication";
  sources: string[];
  cached: boolean;
  degraded: boolean;
  fetched_at: string;
}

export interface Intelligence {
  summary: Summary;
  pipeline: PhaseBucket[];
  sponsors: SponsorShare[];
  timeline: TimelinePoint[];
  status_mix: StatusBucket[];
  regulatory: Regulatory;
  safety: SafetySignal[];
  trials: Trial[];
  brief: Brief;
  meta: Meta;
}

export async function fetchIntelligence(
  query: string,
  refresh = false
): Promise<Intelligence> {
  const url = `/api/intelligence?q=${encodeURIComponent(query)}${
    refresh ? "&refresh=true" : ""
  }`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body.slice(0, 160) || res.statusText}`);
  }
  return res.json();
}
