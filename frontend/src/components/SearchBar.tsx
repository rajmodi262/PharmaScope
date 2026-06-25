import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Loader2 } from "lucide-react";

const EXAMPLES = ["semaglutide", "obesity", "pembrolizumab", "psoriasis", "CAR-T", "Alzheimer"];

export default function SearchBar({
  onSearch,
  loading,
}: {
  onSearch: (q: string) => void;
  loading: boolean;
}) {
  const [value, setValue] = useState("");

  const submit = (q: string) => {
    const term = q.trim();
    if (term.length >= 2 && !loading) onSearch(term);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.form
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        onSubmit={(e) => {
          e.preventDefault();
          submit(value);
        }}
        className="relative group"
      >
        <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-r from-accent-cyan/40 to-accent-violet/40 opacity-0 group-focus-within:opacity-100 blur transition-opacity" />
        <div className="relative flex items-center glass rounded-2xl px-4 py-2">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Search a drug or indication — e.g. semaglutide, obesity, pembrolizumab"
            className="flex-1 bg-transparent outline-none px-3 py-2.5 text-[15px] placeholder:text-slate-500"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || value.trim().length < 2}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-violet px-4 py-2 text-sm font-semibold text-ink-950 disabled:opacity-40 transition hover:brightness-110"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Analyze"}
          </button>
        </div>
      </motion.form>

      <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
        <span className="text-xs text-slate-500">Try:</span>
        {EXAMPLES.map((ex, i) => (
          <motion.button
            key={ex}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.05 }}
            onClick={() => {
              setValue(ex);
              submit(ex);
            }}
            className="rounded-full border border-slate-700/70 bg-ink-800/40 px-3 py-1 text-xs text-slate-300 hover:border-accent-cyan/50 hover:text-accent-cyan transition"
          >
            {ex}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
