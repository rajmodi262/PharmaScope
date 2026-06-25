import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity, Database, Download, AlertCircle, Loader2, Sparkles,
} from "lucide-react";
import { fetchIntelligence, type Intelligence } from "./api";
import SearchBar from "./components/SearchBar";
import StatCards from "./components/StatCards";
import { PipelineFunnel, SponsorChart, MomentumChart } from "./components/Charts";
import AnalystBrief from "./components/AnalystBrief";
import { RegulatoryCard, SafetyPanel } from "./components/RegulatorySafety";
import TrialTable from "./components/TrialTable";

export default function App() {
  const [data, setData] = useState<Intelligence | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const run = async (q: string) => {
    setLoading(true);
    setError(null);
    setQuery(q);
    try {
      setData(await fetchIntelligence(q));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const exportBrief = () => {
    if (!data) return;
    const b = data.brief;
    const md = [
      `# PharmaScope — Competitive Intelligence Brief — ${query}`,
      `_Generated ${data.meta.fetched_at} · Sources: ${data.meta.sources.join(", ")}_\n`,
      `**${data.summary.total_trials.toLocaleString()}** registered trials · ` +
        `**${data.summary.active_trials}** active · ` +
        `**${data.summary.late_stage_trials}** late-stage · ` +
        `**${data.summary.sponsor_count}** sponsors\n`,
      `## Key Insights\n${b.insights.map((x) => `- ${x}`).join("\n")}`,
      `\n## Opportunities\n${b.opportunities.map((x) => `- ${x}`).join("\n")}`,
      `\n## Threats\n${b.threats.map((x) => `- ${x}`).join("\n")}`,
    ].join("\n").replace(/\*\*/g, "**");
    const blob = new Blob([md], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `intel_brief_${query.replace(/\s+/g, "_")}.md`;
    a.click();
  };

  const hasResults = !!data && !loading;

  return (
    <div className="relative min-h-screen">
      <div className="aurora" />

      <div className="relative z-10 max-w-7xl mx-auto px-5 md:px-8 py-6">
        {/* Brand bar */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2.5">
            <div className="grid place-items-center w-9 h-9 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-violet">
              <Activity className="w-5 h-5 text-ink-950" />
            </div>
            <div>
              <div className="font-bold tracking-tight leading-none">
                Pharma<span className="gradient-text">Scope</span>
              </div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                Competitive Intelligence
              </div>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-500">
            <Database className="w-3.5 h-3.5" />
            ClinicalTrials.gov · openFDA · live
          </div>
        </header>

        {/* Hero (collapses once results arrive) */}
        <AnimatePresence>
          {!hasResults && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center pt-10 md:pt-16 pb-8"
            >
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="inline-flex items-center gap-2 rounded-full border border-slate-700/60 bg-ink-800/40 px-3 py-1 text-xs text-slate-400 mb-6"
              >
                <Sparkles className="w-3.5 h-3.5 text-accent-cyan" />
                Live biopharma competitive intelligence
              </motion.div>
              <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.05]">
                Decode any drug's <br />
                <span className="gradient-text">competitive landscape</span>
              </h1>
              <p className="text-slate-400 mt-5 max-w-xl mx-auto text-[15px] leading-relaxed">
                Search a molecule or indication. We pull the live pipeline, sponsors,
                regulatory status and safety signals — and write the analyst brief.
              </p>
              <div className="mt-9">
                <SearchBar onSearch={run} loading={loading} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="relative">
              <Loader2 className="w-10 h-10 text-accent-cyan animate-spin" />
            </div>
            <p className="text-slate-400 text-sm">
              Querying ClinicalTrials.gov & openFDA for{" "}
              <span className="text-white font-medium">{query}</span>…
            </p>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="max-w-lg mx-auto glass p-6 flex items-start gap-3 mt-6 border-accent-rose/30">
            <AlertCircle className="w-5 h-5 text-accent-rose shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-white">Couldn't complete the analysis</p>
              <p className="text-sm text-slate-400 mt-1">{error}</p>
              <button onClick={() => run(query)} className="mt-3 text-sm text-accent-cyan hover:underline">
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {hasResults && data && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
            {/* compact search + title row */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-wider text-slate-500">
                  {data.meta.resolved_type === "drug" ? "Drug" : "Indication"} intelligence
                </div>
                <h2 className="text-3xl font-bold tracking-tight capitalize">{query}</h2>
              </div>
              <div className="flex items-center gap-2 w-full lg:w-auto lg:min-w-[420px]">
                <div className="flex-1">
                  <SearchBar onSearch={run} loading={loading} />
                </div>
              </div>
            </div>

            <StatCards summary={data.summary} />

            {/* Analyst brief — the hero deliverable */}
            <div className="flex items-center justify-between pt-2">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
                Analyst Brief
              </h3>
              <button
                onClick={exportBrief}
                className="flex items-center gap-1.5 rounded-lg border border-slate-700/70 bg-ink-800/40 px-3 py-1.5 text-xs text-slate-300 hover:border-accent-cyan/50 hover:text-accent-cyan transition"
              >
                <Download className="w-3.5 h-3.5" /> Export brief
              </button>
            </div>
            <AnalystBrief brief={data.brief} />

            {/* charts */}
            <div className="grid lg:grid-cols-3 gap-4">
              <PipelineFunnel data={data.pipeline} delay={0} />
              <SponsorChart data={data.sponsors} delay={0.08} />
              <MomentumChart data={data.timeline} delay={0.16} />
            </div>

            <div className="grid lg:grid-cols-2 gap-4">
              <RegulatoryCard reg={data.regulatory} delay={0} />
              <SafetyPanel safety={data.safety} delay={0.08} />
            </div>

            <TrialTable trials={data.trials} delay={0} />

            {/* provenance footer */}
            <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500 pt-4 pb-8">
              <span>
                Sources: {data.meta.sources.join(" · ")} · {data.meta.fetched_at}
                {data.meta.cached && " · cached"}
              </span>
              {data.meta.degraded && (
                <span className="text-accent-amber">⚠ served from fallback (upstream unavailable)</span>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
