"use client";

import { motion } from "framer-motion";
import { ShieldCheck, ChevronRight } from "lucide-react";

export default function LandingHero({ onStart }: { onStart: () => void }) {
  return (
    <section className="relative w-full flex flex-col items-center justify-center pt-24 pb-16 px-4 text-center overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-blue/20 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="glass-card px-4 py-1.5 mb-6 flex items-center gap-2 text-sm text-brand-teal"
      >
        <ShieldCheck className="w-4 h-4" />
        <span>Armor Financial Intelligence V2</span>
      </motion.div>

      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.1 }}
        className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/60"
      >
        Understand Financial <br className="hidden md:block" />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-blue to-brand-teal">
          Conversations Instantly
        </span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl"
      >
        Armor transforms raw multi-lingual conversations into structured financial intelligence. 
        Track commitments, extract insights, and assess risk with zero human effort.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mt-10 flex flex-col sm:flex-row items-center gap-4 z-10"
      >
        <button 
          onClick={onStart}
          className="group relative px-8 py-4 bg-brand-blue text-white rounded-2xl font-semibold shadow-[0_0_40px_rgba(59,130,246,0.4)] hover:shadow-[0_0_60px_rgba(59,130,246,0.6)] transition-all flex items-center gap-2 overflow-hidden"
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
          <span className="relative z-10 text-lg">Start Analysis</span>
          <ChevronRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform" />
        </button>
        
        <button 
          onClick={onStart}
          className="px-8 py-4 glass-card text-foreground font-semibold hover:bg-white/10 transition-colors text-lg"
        >
          View Demo
        </button>
      </motion.div>
    </section>
  );
}
