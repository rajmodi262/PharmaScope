import { ShieldCheck, Pill, AlertOctagon } from "lucide-react";
import type { Regulatory, SafetySignal } from "../api";
import Panel from "./Panel";

export function RegulatoryCard({ reg, delay }: { reg: Regulatory; delay: number }) {
  return (
    <Panel
      title="Regulatory profile"
      subtitle="openFDA drug label"
      icon={<ShieldCheck className="w-5 h-5" />}
      delay={delay}
    >
      {reg.approved ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {reg.brand_names.map((b) => (
              <span key={b} className="flex items-center gap-1.5 rounded-lg bg-accent-emerald/10 border border-accent-emerald/30 px-3 py-1.5 text-sm font-semibold text-accent-emerald">
                <Pill className="w-3.5 h-3.5" /> {b}
              </span>
            ))}
          </div>
          <div className="text-sm text-slate-400">
            <span className="text-slate-500">Manufacturer · </span>
            {reg.manufacturers.join(", ") || "—"}
          </div>
          {reg.routes.length > 0 && (
            <div className="text-sm text-slate-400">
              <span className="text-slate-500">Route · </span>
              {reg.routes.join(", ")}
            </div>
          )}
          {reg.indication && (
            <p className="text-[13px] leading-relaxed text-slate-300 border-l-2 border-accent-cyan/40 pl-3">
              {reg.indication}
            </p>
          )}
        </div>
      ) : (
        <div className="text-sm text-slate-400">
          No approved FDA label matched this query — likely investigational,
          pre-approval, or an indication-level search.
        </div>
      )}
    </Panel>
  );
}

export function SafetyPanel({ safety, delay }: { safety: SafetySignal[]; delay: number }) {
  const max = Math.max(...safety.map((s) => s.count), 1);
  return (
    <Panel
      title="Real-world safety signals"
      subtitle="Top FAERS adverse-event reports"
      icon={<AlertOctagon className="w-5 h-5" />}
      delay={delay}
    >
      {safety.length === 0 ? (
        <div className="text-sm text-slate-400">No aggregated adverse-event data available.</div>
      ) : (
        <ul className="space-y-2.5">
          {safety.slice(0, 7).map((s) => (
            <li key={s.reaction}>
              <div className="flex justify-between text-[13px] mb-1">
                <span className="text-slate-300">{s.reaction}</span>
                <span className="font-mono text-slate-400">{s.count.toLocaleString()}</span>
              </div>
              <div className="h-1.5 rounded-full bg-ink-700/60 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-accent-amber to-accent-rose"
                  style={{ width: `${(s.count / max) * 100}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
