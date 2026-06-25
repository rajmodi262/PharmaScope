import { motion } from "framer-motion";
import { Lightbulb, Rocket, AlertTriangle } from "lucide-react";
import type { Brief } from "../api";

// Render **bold** spans from the rule-based brief markdown.
function RichText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          <strong key={i} className="text-white font-semibold">{p.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </>
  );
}

function Column({
  title,
  items,
  icon,
  accent,
  delay,
}: {
  title: string;
  items: string[];
  icon: React.ReactNode;
  accent: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="glass p-5 flex flex-col"
    >
      <div className="flex items-center gap-2 mb-4">
        <div
          className="grid place-items-center w-8 h-8 rounded-lg"
          style={{ background: `${accent}1f`, color: accent }}
        >
          {icon}
        </div>
        <h4 className="font-semibold text-white">{title}</h4>
      </div>
      <ul className="space-y-3">
        {items.map((it, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -8 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: delay + 0.1 + i * 0.07 }}
            className="flex gap-2.5 text-[13.5px] leading-relaxed text-slate-300"
          >
            <span className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0" style={{ background: accent }} />
            <span><RichText text={it} /></span>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}

export default function AnalystBrief({ brief }: { brief: Brief }) {
  return (
    <div className="grid md:grid-cols-3 gap-4">
      <Column title="Key Insights" items={brief.insights} icon={<Lightbulb className="w-4 h-4" />} accent="#22d3ee" delay={0} />
      <Column title="Opportunities" items={brief.opportunities} icon={<Rocket className="w-4 h-4" />} accent="#34d399" delay={0.1} />
      <Column title="Threats" items={brief.threats} icon={<AlertTriangle className="w-4 h-4" />} accent="#fb7185" delay={0.2} />
    </div>
  );
}
