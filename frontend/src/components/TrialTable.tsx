import { useState } from "react";
import { ExternalLink, ListFilter } from "lucide-react";
import type { Trial } from "../api";
import Panel from "./Panel";

const STATUS_COLOR: Record<string, string> = {
  RECRUITING: "#34d399",
  ACTIVE_NOT_RECRUITING: "#22d3ee",
  NOT_YET_RECRUITING: "#fbbf24",
  COMPLETED: "#94a3b8",
  TERMINATED: "#fb7185",
  WITHDRAWN: "#fb7185",
};

export default function TrialTable({ trials, delay }: { trials: Trial[]; delay: number }) {
  const [showAll, setShowAll] = useState(false);
  const rows = showAll ? trials : trials.slice(0, 8);

  return (
    <Panel
      title="Trial register"
      subtitle={`${trials.length} most recently updated studies`}
      icon={<ListFilter className="w-5 h-5" />}
      delay={delay}
    >
      <div className="overflow-x-auto -mx-2">
        <table className="w-full text-[13px] border-collapse">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-700/50">
              <th className="py-2 px-2 font-medium">Study</th>
              <th className="py-2 px-2 font-medium">Phase</th>
              <th className="py-2 px-2 font-medium">Status</th>
              <th className="py-2 px-2 font-medium">Sponsor</th>
              <th className="py-2 px-2 font-medium text-right">N</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={t.nct_id} className="border-b border-slate-800/50 hover:bg-ink-800/40 transition">
                <td className="py-2.5 px-2 max-w-[340px]">
                  <a
                    href={`https://clinicaltrials.gov/study/${t.nct_id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-200 hover:text-accent-cyan transition flex items-start gap-1 group"
                  >
                    <span className="line-clamp-2">{t.title}</span>
                    <ExternalLink className="w-3 h-3 mt-0.5 opacity-0 group-hover:opacity-60 shrink-0" />
                  </a>
                  <span className="font-mono text-[11px] text-slate-500">{t.nct_id}</span>
                </td>
                <td className="py-2.5 px-2 whitespace-nowrap text-slate-300">{t.phase}</td>
                <td className="py-2.5 px-2 whitespace-nowrap">
                  <span
                    className="inline-flex items-center gap-1.5 text-xs"
                    style={{ color: STATUS_COLOR[t.status] || "#cbd5e1" }}
                  >
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: STATUS_COLOR[t.status] || "#cbd5e1" }} />
                    {t.status.replace(/_/g, " ").toLowerCase()}
                  </span>
                </td>
                <td className="py-2.5 px-2 text-slate-400 max-w-[180px] truncate">{t.sponsor}</td>
                <td className="py-2.5 px-2 text-right font-mono text-slate-400">
                  {t.enrollment?.toLocaleString() ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {trials.length > 8 && (
        <button
          onClick={() => setShowAll((s) => !s)}
          className="mt-4 text-xs text-accent-cyan hover:underline"
        >
          {showAll ? "Show less" : `Show all ${trials.length} studies`}
        </button>
      )}
    </Panel>
  );
}
