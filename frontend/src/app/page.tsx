"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import LandingHero from "@/components/LandingHero";
import Dashboard from "@/components/Dashboard";

export default function Home() {
  const [started, setStarted] = useState(false);

  return (
    <div className="min-h-screen flex flex-col items-center overflow-x-hidden">
      {/* Navbar overlay */}
      <nav className="w-full p-6 flex justify-between items-center z-50">
        <div className="flex items-center gap-3 font-bold text-xl tracking-tight mx-auto max-w-7xl w-full">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-blue to-brand-teal flex items-center justify-center shadow-lg shadow-brand-blue/20 border border-white/20">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
          </div>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70 tracking-wide text-2xl">Armor</span>
        </div>
      </nav>

      <main className="flex-1 w-full relative z-10 flex flex-col justify-center">
        <AnimatePresence mode="wait">
          {!started ? (
            <motion.div 
              key="landing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.5 }}
              className="w-full flex-1 flex items-center justify-center"
            >
              <LandingHero onStart={() => setStarted(true)} />
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="w-full h-full flex flex-col pt-8"
            >
              <Dashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="w-full flex gap-6 flex-wrap items-center justify-center text-muted-foreground p-8 text-sm opacity-60">
        Team Axon • DSAI Society IIIT Dharwad 2026
      </footer>
    </div>
  );
}
