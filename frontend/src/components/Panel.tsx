import { motion } from "framer-motion";

export default function Panel({
  title,
  subtitle,
  icon,
  children,
  className = "",
  delay = 0,
}: {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] }}
      className={`glass p-6 ${className}`}
    >
      <div className="flex items-start gap-3 mb-5">
        {icon && (
          <div className="mt-0.5 text-accent-cyan">{icon}</div>
        )}
        <div>
          <h3 className="text-[15px] font-semibold text-white tracking-tight">{title}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {children}
    </motion.section>
  );
}
