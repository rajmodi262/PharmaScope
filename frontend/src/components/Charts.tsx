import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip,
  AreaChart, Area, CartesianGrid,
} from "recharts";
import { GitBranch, Trophy, TrendingUp } from "lucide-react";
import type { PhaseBucket, SponsorShare, TimelinePoint } from "../api";
import Panel from "./Panel";

const PHASE_COLORS = ["#22d3ee", "#38bdf8", "#a855f7", "#fbbf24"];

const tooltipStyle = {
  background: "rgba(10,16,36,0.95)",
  border: "1px solid rgba(148,163,184,0.2)",
  borderRadius: 12,
  color: "#e2e8f0",
  fontSize: 12,
};

export function PipelineFunnel({ data, delay }: { data: PhaseBucket[]; delay: number }) {
  return (
    <Panel
      title="Development pipeline"
      subtitle="Trials by most-advanced phase"
      icon={<GitBranch className="w-5 h-5" />}
      delay={delay}
    >
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
          <XAxis dataKey="phase" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(148,163,184,0.08)" }} />
          <Bar dataKey="count" radius={[8, 8, 0, 0]} maxBarSize={64}>
            {data.map((_, i) => (
              <Cell key={i} fill={PHASE_COLORS[i % PHASE_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  );
}

export function SponsorChart({ data, delay }: { data: SponsorShare[]; delay: number }) {
  const trimmed = data.slice(0, 6).map((d) => ({
    ...d,
    short: d.name.length > 22 ? d.name.slice(0, 21) + "…" : d.name,
  }));
  return (
    <Panel
      title="Competitive landscape"
      subtitle="Lead sponsors by trial volume"
      icon={<Trophy className="w-5 h-5" />}
      delay={delay}
    >
      <ResponsiveContainer width="100%" height={240}>
        <BarChart layout="vertical" data={trimmed} margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="short"
            tick={{ fill: "#cbd5e1", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={140}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            cursor={{ fill: "rgba(148,163,184,0.08)" }}
            formatter={(v: number, _n, p: any) => [`${v} trials · ${p.payload.share}%`, "Activity"]}
          />
          <Bar dataKey="trials" radius={[0, 6, 6, 0]} maxBarSize={22}>
            {trimmed.map((_, i) => (
              <Cell key={i} fill={i === 0 ? "#a855f7" : "#38bdf8"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  );
}

export function MomentumChart({ data, delay }: { data: TimelinePoint[]; delay: number }) {
  return (
    <Panel
      title="Research momentum"
      subtitle="New trial starts per year"
      icon={<TrendingUp className="w-5 h-5" />}
      delay={delay}
    >
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
          <defs>
            <linearGradient id="momentum" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ stroke: "rgba(34,211,238,0.3)" }} />
          <Area
            type="monotone"
            dataKey="starts"
            stroke="#22d3ee"
            strokeWidth={2.5}
            fill="url(#momentum)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Panel>
  );
}
