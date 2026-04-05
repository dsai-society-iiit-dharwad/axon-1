"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Upload, Cloud, Lock, Loader2, Sparkles, AlertTriangle, Square, Radio } from "lucide-react";
import TranscriptView from "./TranscriptView";
import InsightsPanel from "./InsightsPanel";
import AISummary from "./AISummary";
import StructuredOutput from "./StructuredOutput";
import HistoryDashboard from "./HistoryDashboard";

type ProcessingStep = "idle" | "listening" | "transcribing" | "extracting" | "summarizing" | "done";

export default function Dashboard() {
  const [view, setView] = useState<"analysis" | "history">("analysis");
  const [mode, setMode] = useState<"local" | "cloud">("cloud");
  const [groqKey, setGroqKey] = useState("");
  const [step, setStep] = useState<ProcessingStep>("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Live recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks to release mic
        stream.getTracks().forEach(t => t.stop());
        
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        const audioFile = new File([audioBlob], "recording.webm", { type: "audio/webm" });

        // Now send to backend
        setStep("transcribing");
        setError(null);
        setResult(null);

        const t1 = setTimeout(() => setStep("extracting"), 3000);
        const t2 = setTimeout(() => setStep("summarizing"), 6000);

        try {
          const formData = new FormData();
          formData.append("backend", mode);
          formData.append("file", audioFile);

          const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: formData });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || `Server error: ${res.statusText}`);
          
          clearTimeout(t1);
          clearTimeout(t2);
          setResult(data);
          setStep("done");
        } catch (err: any) {
          clearTimeout(t1);
          clearTimeout(t2);
          setError(err.message || "Failed to analyze");
          setStep("idle");
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setResult(null);
      setStep("listening");

      // Start elapsed timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err) {
      setError("Microphone access denied. Please allow mic permission.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  const runAnalysis = async (type: "demo" | "upload" | "mic") => {
    setStep("transcribing");
    setError(null);
    setResult(null);

    const t1 = setTimeout(() => { if (step !== "done") setStep("extracting"); }, 2000);
    const t2 = setTimeout(() => { if (step !== "done") setStep("summarizing"); }, 4000);

    try {
      const formData = new FormData();
      formData.append("backend", mode);

      if (type === "demo") {
        formData.append("demo", "true");
      } else {
        formData.append("demo", "true"); // For now just forcing demo
      }

      const res = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Server error: ${res.statusText}`);
      
      clearTimeout(t1);
      clearTimeout(t2);
      setResult(data);
      setStep("done");
    } catch (err: any) {
      clearTimeout(t1);
      clearTimeout(t2);
      setError(err.message || "Failed to analyze");
      setStep("idle");
    }
  };

  const stepsList = [
    { id: "listening", label: "Listening to Conversation" },
    { id: "transcribing", label: "Transcribing Audio & Language" },
    { id: "extracting", label: "Extracting Financial Entities" },
    { id: "summarizing", label: "Generating LLaMA Intelligence" },
  ];

  const loadHistoryDetail = async (id: number) => {
    try {
      setStep("transcribing"); // show loading state momentarily
      setView("analysis"); // switch back to analysis view
      const res = await fetch(`http://localhost:8000/api/history/${id}`);
      if (!res.ok) throw new Error("Failed to load conversation");
      const data = await res.json();
      setResult(data);
      setStep("done");
    } catch (err: any) {
      setError(err.message);
      setStep("idle");
    }
  };

  return (
    <div className="w-full max-w-[1400px] mx-auto px-6 pb-20 mt-8">
      
      {/* Top View Toggle */}
      <div className="flex justify-between items-end mb-8 border-b border-white/10 pb-4">
        <div>
           <h2 className="text-xl font-bold text-white tracking-tight">Intelligence Engine</h2>
           <p className="text-sm text-muted-foreground mt-1">Live capture and financial insight extraction</p>
        </div>
        <div className="bg-[#111] p-1 rounded-md flex border border-white/10 max-w-[300px]">
          <button
            onClick={() => setView("analysis")}
            className={`px-4 py-1.5 rounded text-xs font-semibold tracking-wide transition-all ${
              view === "analysis" ? "bg-white/10 text-white shadow-sm border border-white/5" : "text-muted-foreground hover:text-white"
            }`}
          >
            Terminal
          </button>
          <button
            onClick={() => setView("history")}
            className={`px-4 py-1.5 rounded text-xs font-semibold tracking-wide transition-all ${
              view === "history" ? "bg-white/10 text-white shadow-sm border border-white/5" : "text-muted-foreground hover:text-white"
            }`}
          >
            Vault Hub
          </button>
        </div>
      </div>

      {view === "history" ? (
        <div className="h-full min-h-[600px] w-full animate-in fade-in">
          <HistoryDashboard onViewDetail={loadHistoryDetail} />
        </div>
      ) : (
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 auto-rows-min">
        
        {/* LEFT PANEL: BENTO RECORDING CONTROL */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-[#0A0A0A] border border-[var(--border)] rounded-xl p-5 shadow-2xl flex flex-col h-full">
            <div className="flex items-center justify-between mb-6">
              <span className="text-xs uppercase tracking-widest text-muted-foreground font-semibold flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-white/40" /> Settings
              </span>
            </div>

            <div className="flex bg-[#111] rounded-md p-1 mb-6 border border-white/5">
              <button
                onClick={() => setMode("local")}
                className={`flex-1 py-1.5 rounded text-xs font-medium transition-all flex items-center justify-center gap-2 ${
                  mode === "local" ? "bg-white/15 text-white" : "text-muted-foreground hover:text-white"
                }`}
              >
                <Lock className="w-3.5 h-3.5" /> Edge
              </button>
              <button
                onClick={() => setMode("cloud")}
                className={`flex-1 py-1.5 rounded text-xs font-medium transition-all flex items-center justify-center gap-2 ${
                  mode === "cloud" ? "bg-brand-teal text-black" : "text-muted-foreground hover:text-white"
                }`}
              >
                <Cloud className="w-3.5 h-3.5" /> Cloud
              </button>
            </div>

            <div className="space-y-2 mt-auto">
              {/* 🎙️ RECORD LIVE */}
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  disabled={step !== "idle" && step !== "done"}
                  className="w-full relative group bg-white hover:bg-white/90 border border-transparent text-black rounded-lg p-3 flex justify-between items-center transition-all disabled:opacity-50"
               >
                  <div className="flex items-center gap-3">
                    <Radio className="w-4 h-4 text-brand-teal" />
                    <span className="text-sm font-bold tracking-tight">Initialize Mic</span>
                  </div>
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="w-full relative group bg-red-500 hover:bg-red-600 text-white rounded-lg p-3 flex justify-between items-center transition-all animate-pulse"
                >
                  <div className="flex items-center gap-3">
                    <Square className="w-4 h-4" />
                    <span className="text-sm font-bold tracking-tight">Stop Target</span>
                  </div>
                  <span className="text-xs font-mono">{formatTime(recordingTime)}</span>
                </button>
              )}

              {/* Demo Audio */}
              <button
                onClick={() => runAnalysis("demo")}
                disabled={(step !== "idle" && step !== "done") || isRecording}
                className="w-full bg-[#151515] hover:bg-[#222] border border-[var(--border)] rounded-lg p-3 flex items-center gap-3 transition-all disabled:opacity-50"
              >
                <Mic className="w-4 h-4 text-white/50" />
                <span className="text-sm font-medium text-white/80 tracking-tight">Simulate (Arjun & Priya)</span>
              </button>

              {/* Upload Audio */}
              <label
                className={`w-full bg-[#151515] hover:bg-[#222] border border-[var(--border)] rounded-lg p-3 flex items-center gap-3 transition-all ${
                  (step !== "idle" && step !== "done") || isRecording ? "opacity-50 cursor-not-allowed hidden" : "cursor-pointer"
                }`}
              >
                <input 
                   type="file" 
                   accept="audio/wav, audio/mpeg, audio/mp3, audio/m4a, audio/webm"
                   className="hidden" 
                   disabled={(step !== "idle" && step !== "done") || isRecording}
                   onChange={async (e) => {
                     // Keep exact file upload logic intact
                     if (e.target.files && e.target.files.length > 0) {
                        const file = e.target.files[0];
                        setStep("transcribing");
                        setError(null);
                        setResult(null);

                        const t1 = setTimeout(() => setStep("extracting"), 2000);
                        const t2 = setTimeout(() => setStep("summarizing"), 4000);

                        try {
                          const formData = new FormData();
                          formData.append("backend", mode);
                          formData.append("file", file);

                          const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: formData });
                          const data = await res.json();
                          if (!res.ok) throw new Error(data.detail || `Server error: ${res.statusText}`);
                          
                          clearTimeout(t1);
                          clearTimeout(t2);
                          setResult(data);
                          setStep("done");
                        } catch (err: any) {
                          clearTimeout(t1);
                          clearTimeout(t2);
                          setError(err.message || "Failed to analyze");
                          setStep("idle");
                        }
                     }
                   }}
                />
                <Upload className="w-4 h-4 text-white/50" />
                <span className="text-sm font-medium text-white/80 tracking-tight">Upload Asset</span>
              </label>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-2 text-red-500 text-sm">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL: BENTO RESULTS */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          {step === "idle" && !result && (
             <div className="h-full min-h-[400px] bg-[#0A0A0A] border border-[var(--border)] rounded-xl flex flex-col items-center justify-center text-muted-foreground shadow-2xl">
               <span className="text-xs font-mono uppercase tracking-widest text-white/30 border border-white/5 py-1 px-3 rounded">Armor Engine</span>
               <p className="mt-4 text-sm text-white/40">Select an input method to begin</p>
             </div>
          )}

          {step !== "idle" && step !== "done" && (
            <div className="bg-[#0A0A0A] border border-[var(--border)] rounded-xl p-8 min-h-[400px] flex flex-col justify-center">
              <h2 className="text-lg font-bold mb-8 text-center text-white tracking-tight">
                Processing Thread
              </h2>
              <div className="space-y-4 max-w-sm mx-auto w-full">
                {stepsList.map((s, i) => {
                  const isActive = step === s.id;
                  const isPast = stepsList.findIndex((x) => x.id === step) > i;
                  return (
                    <div key={s.id} className="flex items-center gap-4 py-2 border-b border-[var(--border)] last:border-0">
                      <div className={`w-6 h-6 rounded flex items-center justify-center text-xs transition-colors duration-500 font-mono ${
                        isActive ? "bg-white text-black" : 
                        isPast ? "bg-brand-teal text-black" : "bg-white/5 text-muted-foreground"
                      }`}>
                        {isActive ? <Loader2 className="w-3 h-3 animate-spin" /> : 
                         isPast ? <span>✓</span> : 
                         <span>{i + 1}</span>}
                      </div>
                      <span className={`text-sm tracking-tight transition-colors duration-500 ${
                        isActive ? "text-white font-medium" : 
                        isPast ? "text-white/70" : "text-muted-foreground"
                      }`}>
                        {s.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {step === "done" && result && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {!result.is_financial && (
                 <div className="bg-red-500/10 border border-red-500/20 text-red-500 px-6 py-4 rounded-2xl flex items-center gap-3">
                   <AlertTriangle className="w-6 h-6 shrink-0" />
                   <div>
                     <h4 className="font-bold">Non-Financial Conversation Detected</h4>
                     <p className="text-sm opacity-90">Armor bypassed generation. AI matched with confidence {(result.fin_score * 100).toFixed(0)}%.</p>
                   </div>
                 </div>
              )}
              
              <StructuredOutput result={result} />
              <AISummary summary={result.summary} isFinancial={result.is_financial} />
              <InsightsPanel entities={result.entities} />
              <TranscriptView turns={result.turns} entities={result.entities} />
            </motion.div>
          )}
        </div>

      </div>
      )}
    </div>
  );
}

const ShieldIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
  </svg>
);
