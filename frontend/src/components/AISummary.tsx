"use client";

import { motion } from "framer-motion";
import { CheckCircle2, CircleDashed } from "lucide-react";

export default function AISummary({ summary, isFinancial }: { summary: any; isFinancial: boolean }) {
  if (!isFinancial || !summary || !summary.risk_label) return null;

  const getRiskColor = (label: string) => {
    switch (label) {
      case "Low": return "text-green-500 bg-green-500/10 border-green-500/20";
      case "Medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "High": return "text-red-500 bg-red-500/10 border-red-500/20";
      default: return "text-gray-500 bg-gray-500/10 border-gray-500/20";
    }
  };

  const getBarColor = (label: string) => {
    switch (label) {
      case "Low": return "bg-green-500";
      case "Medium": return "bg-yellow-500";
      case "High": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const commitments = summary.commitments || [];
  const decisions = summary.pending_decisions || [];

  return (
    <div className="glass-card p-6 md:p-8 relative overflow-hidden">
      {/* background glow */}
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-brand-blue/10 rounded-full blur-[80px]" />

      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-blue to-brand-teal">
          AI Financial Intelligence
        </span>
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Risk Score */}
        <div className={`col-span-1 rounded-2xl border p-6 flex flex-col items-center justify-center text-center ${getRiskColor(summary.risk_label)}`}>
          <h3 className="text-sm font-semibold uppercase tracking-wider mb-4 opacity-80">Risk Assessment</h3>
          <div className="text-5xl font-black mb-2">{summary.risk_score}</div>
          <div className="text-lg font-bold mb-4">{summary.risk_label} Risk</div>
          
          <div className="w-full bg-black/20 h-2 rounded-full overflow-hidden mb-4">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(summary.risk_score, 100)}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-full ${getBarColor(summary.risk_label)}`}
            />
          </div>
          
          <p className="text-xs opacity-90">{summary.risk_reasoning}</p>
        </div>

        {/* Commitments & Decisions */}
        <div className="col-span-1 lg:col-span-2 space-y-6">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-brand-teal" />
              Commitments Extracted
            </h3>
            {commitments.length > 0 ? (
              <ul className="space-y-3">
                {commitments.map((c: any, i: number) => (
                  <motion.li 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    key={i} 
                    className="bg-white/5 rounded-xl p-3 text-sm flex flex-col sm:flex-row sm:items-center gap-2"
                  >
                    <span className="bg-white/10 px-2 py-0.5 rounded text-xs font-semibold shrink-0">{c.speaker}</span>
                    <span className="text-white/90">{c.commitment}</span>
                  </motion.li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground italic">No solid commitments detected.</p>
            )}
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
              <CircleDashed className="w-4 h-4 text-brand-blue" />
              Pending Decisions
            </h3>
            {decisions.length > 0 ? (
              <ul className="list-disc list-inside space-y-1">
                {decisions.map((d: string, i: number) => (
                  <li key={i} className="text-sm text-white/80">{d}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground italic">No pending decisions.</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
