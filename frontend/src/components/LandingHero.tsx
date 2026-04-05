"use client";

import { motion } from "framer-motion";
import { ShieldCheck, ChevronRight, Zap, Target } from "lucide-react";

export default function LandingHero({ onStart }: { onStart: () => void }) {
  return (
    <section className="relative w-full flex flex-col items-center justify-center pt-32 pb-24 overflow-hidden min-h-screen bg-black">
      
      {/* Background Grid - Extremely subtle */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#222_1px,transparent_1px),linear-gradient(to_bottom,#222_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      <div className="container relative z-10 mx-auto px-6 max-w-6xl flex flex-col items-center text-center">
        
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs text-muted-foreground font-medium mb-8 uppercase tracking-widest backdrop-blur-sm"
        >
          <Target className="w-3.5 h-3.5 text-brand-teal" />
          <span>Armor Intelligence • v2.0</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl md:text-7xl font-sans font-extrabold tracking-tighter text-white mb-6 leading-[1.05]"
        >
          Conversations into <br />
          <span className="text-brand-teal">Structured Intelligence</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl font-sans tracking-tight"
        >
          Capture informal Hinglish commitments. Armor extracts amounts, SIP timelines, and risk metrics via edge-deployed LLMs with zero human intervention.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center gap-4"
        >
          <button 
            onClick={onStart}
            className="group px-6 py-3 bg-white text-black border border-transparent rounded-lg font-semibold hover:bg-white/90 transition-all flex items-center justify-center gap-2"
          >
            Start Analysis Engine
            <ChevronRight className="w-4 h-4 text-black/50 group-hover:translate-x-0.5 transition-transform" />
          </button>
          
          <button className="px-6 py-3 bg-transparent border border-white/10 text-white rounded-lg font-medium hover:bg-white/5 transition-colors flex items-center gap-2">
            View Live Demo
          </button>
        </motion.div>

        {/* Minimalist Tech Stats */}
        <motion.div 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          className="mt-16 pt-8 border-t border-white/5 w-full max-w-3xl flex justify-center gap-12 text-sm text-muted-foreground"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-brand-teal" />
            <span><strong className="text-white">100%</strong> Offline Ready</span>
          </div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-brand-teal" />
            <span>Bank-Grade Encryption</span>
          </div>
        </motion.div>

        {/* The Sleek "WhatsApp" Demonstration (Expert Aesthetic) */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-20 w-full max-w-3xl relative mx-auto"
        >
          {/* Faded glow behind the chat */}
          <div className="absolute inset-0 bg-brand-teal/5 blur-3xl pointer-events-none rounded-full" />
          
          <div className="relative glass-panel rounded-xl p-6 border border-white/10 bg-[#0A0A0A] flex flex-col gap-4 text-left shadow-2xl">
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-brand-teal animate-pulse" />
                <span className="text-xs font-mono text-muted-foreground uppercase tracking-widest">Live Capture</span>
              </div>
              <span className="text-xs text-muted-foreground">arjun_priya_09.wav</span>
            </div>

            {/* Tight, minimalist chat bubbles */}
            <div className="flex w-full">
               <div className="bg-[#111] border border-white/5 text-sm text-foreground p-3 rounded-lg rounded-tl-sm max-w-[70%]">
                 "Yaar, SIP shuru kar lete hain? Car loan ki EMI ₹12,000 hai abhi."
               </div>
            </div>

            <div className="flex w-full justify-end">
               <div className="bg-[#151515] border border-brand-teal/20 text-sm text-brand-teal p-3 rounded-lg rounded-tr-sm max-w-[70%]">
                 "Haan, ₹5,000 se start karte hain March tak."
               </div>
            </div>

            <div className="flex w-full mt-4 justify-center">
              <div className="px-3 py-1.5 rounded bg-brand-teal/10 border border-brand-teal/20 text-brand-teal text-xs font-mono flex items-center gap-2">
                <ShieldCheck className="w-3 h-3" />
                Entity Extracted: [SIP: ₹5,000, Timeline: March]
              </div>
            </div>

          </div>
        </motion.div>

      </div>
    </section>
  );
}
