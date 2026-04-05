"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Clock, TrendingUp, Users, AlertTriangle, ShieldCheck, Activity } from "lucide-react";

type ConversationHistory = {
  id: number;
  language: string;
  duration_sec: number;
  speaker_count: number;
  created_at: string;
};

export default function HistoryDashboard({ onViewDetail }: { onViewDetail: (id: number) => void }) {
  const [history, setHistory] = useState<ConversationHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/history")
      .then((res) => res.json())
      .then((data) => {
        setHistory(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const totalTime = history.reduce((acc, curr) => acc + curr.duration_sec, 0);
  const formattedMinutes = Math.floor(totalTime / 60);

  if (loading) {
    return (
      <div className="flex-1 w-full flex items-center justify-center min-h-[500px]">
        <div className="flex flex-col items-center gap-4 text-brand-teal">
          <Activity className="w-8 h-8 animate-spin" />
          <p>Loading global intelligence vault...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col gap-6 animate-in fade-in duration-500">
      
      <div className="flex justify-between items-end mb-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Intelligence Vault</h2>
          <p className="text-sm text-muted-foreground mt-1">Aggregated financial history and analysis</p>
        </div>
      </div>

      {/* Expert Mini-Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }} className="bg-[#0A0A0A] border border-[var(--border)] p-4 flex flex-col rounded-xl">
          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold flex items-center justify-between mb-2">
            Total Conversations <TrendingUp className="w-3 h-3 text-brand-teal" />
          </div>
          <div className="text-2xl font-bold text-white">{history.length}</div>
        </motion.div>
        
        <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }} className="bg-[#0A0A0A] border border-[var(--border)] p-4 flex flex-col rounded-xl">
          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold flex items-center justify-between mb-2">
            Audio Processed <Clock className="w-3 h-3 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-white">{formattedMinutes} <span className="text-sm font-medium text-muted-foreground">min</span></div>
        </motion.div>

        <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }} className="bg-[#0A0A0A] border border-[var(--border)] p-4 flex flex-col rounded-xl">
          <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold flex items-center justify-between mb-2">
            Edge Encryption <ShieldCheck className="w-3 h-3 text-brand-teal" />
          </div>
          <div className="text-2xl font-bold text-white">100%</div>
        </motion.div>
      </div>

      {/* High-Density Data Table */}
      <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.4 }} className="bg-[#0A0A0A] border border-[var(--border)] rounded-xl flex-1 mt-4 overflow-hidden flex flex-col shadow-xl">
        {/* Table Header */}
        <div className="px-5 py-3 border-b border-[#222] bg-[#111] grid grid-cols-6 gap-4 text-[10px] font-semibold text-muted-foreground uppercase tracking-widest">
          <div className="col-span-2">ID / Time</div>
          <div>Language</div>
          <div>Speakers</div>
          <div>Duration</div>
          <div className="text-right">Action</div>
        </div>
        
        {/* Table Body */}
        <div className="overflow-y-auto flex-1 flex flex-col">
          {history.length === 0 ? (
            <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
              Vault is empty. Run an analysis.
            </div>
          ) : (
            history.map((conv, idx) => (
              <motion.div 
                key={conv.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + (idx * 0.03) }}
                className="grid grid-cols-6 gap-4 items-center px-5 py-3 border-b border-[#1A1A1A] hover:bg-[#1A1A1A]/50 transition-colors group"
              >
                <div className="col-span-2 flex items-center gap-3">
                  <div className="w-6 h-6 rounded bg-[#222] border border-[#333] flex items-center justify-center group-hover:border-brand-teal/50 transition-colors">
                    <Users className="w-3 h-3 text-muted-foreground group-hover:text-brand-teal" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-white/90 group-hover:text-white transition-colors">Conversation {conv.id}</span>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{new Date(conv.created_at).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <span className="bg-[#222] border border-[#333] text-white/70 px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide">
                    {conv.language || "Unknown"}
                  </span>
                </div>

                <div className="text-xs font-mono text-white/70">
                  {conv.speaker_count} spk
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground">
                    {Math.round(conv.duration_sec)}s
                  </span>
                  {/* Subtle Sparkline imitation */}
                  <div className="w-12 h-1 bg-[#222] rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500/50" style={{ width: `${Math.min((conv.duration_sec/300)*100, 100)}%` }} />
                  </div>
                </div>

                <div className="text-right">
                  <button 
                    onClick={() => onViewDetail(conv.id)}
                    className="text-xs font-semibold text-brand-teal opacity-60 hover:opacity-100 bg-brand-teal/10 hover:bg-brand-teal/20 border border-transparent hover:border-brand-teal/20 px-3 py-1.5 rounded transition-all disabled:opacity-30"
                  >
                    View Report
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </motion.div>

    </div>
  );
}
