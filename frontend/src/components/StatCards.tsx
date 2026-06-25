import { motion } from "framer-motion";
import { Activity, FlaskConical, Beaker, Building2, BadgeCheck } from "lucide-react";
import type { Summary } from "../api";
import AnimatedNumber from "./AnimatedNumber";

const fade = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0 },
};

function Card({
  icon,
  label,
  value,
  accent,
  suffix,
  delay,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  accent: string;
  suffix?: string;
  delay: number;
}) {
  return (
    <motion.div
      variants={fade}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4 }}
      className="glass p-5 relative overflow-hidden"
    >
      <div
        className="absolute top-0 left-0 h-[3px] w-full opacity-80"
        style={{ background: accent }}
      />
      <div className="flex items-center gap-2 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
        <span style={{ color: accent }}>{icon}</span>
        {label}
      </div>
      <div className="mt-3 font-mono text-3xl font-bold text-white tabular-nums">
        <AnimatedNumber value={value} />
        {suffix}
      </div>
    </motion.div>
  );
}

export default function StatCards({ summary }: { summary: Summary }) {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-5 gap-4"
    >
      <Card icon={<FlaskConical className="w-4 h-4" />} label="Registered trials" value={summary.total_trials} accent="#22d3ee" delay={0} />
      <Card icon={<Activity className="w-4 h-4" />} label="Active / recruiting" value={summary.active_trials} accent="#34d399" delay={0.06} />
      <Card icon={<Beaker className="w-4 h-4" />} label="Late-stage (Ph 3/4)" value={summary.late_stage_trials} accent="#fbbf24" delay={0.12} />
      <Card icon={<Building2 className="w-4 h-4" />} label="Distinct sponsors" value={summary.sponsor_count} accent="#a855f7" delay={0.18} />
      <motion.div
        variants={fade}
        transition={{ duration: 0.5, delay: 0.24, ease: [0.16, 1, 0.3, 1] }}
        whileHover={{ y: -4 }}
        className="glass p-5 relative overflow-hidden col-span-2 md:col-span-1"
      >
        <div
          className="absolute top-0 left-0 h-[3px] w-full"
          style={{ background: summary.approved ? "#34d399" : "#fb7185" }}
        />
        <div className="flex items-center gap-2 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
          <BadgeCheck className="w-4 h-4" style={{ color: summary.approved ? "#34d399" : "#fb7185" }} />
          FDA status
        </div>
        <div className="mt-3 text-2xl font-bold text-white">
          {summary.approved ? "On market" : "No approval"}
        </div>
      </motion.div>
    </motion.div>
  );
}
