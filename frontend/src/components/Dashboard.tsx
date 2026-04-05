"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Upload, Cloud, Lock, Loader2, Sparkles, AlertTriangle, Square, Radio } from "lucide-react";
import TranscriptView from "./TranscriptView";
import InsightsPanel from "./InsightsPanel";
import AISummary from "./AISummary";
import StructuredOutput from "./StructuredOutput";

type ProcessingStep = "idle" | "listening" | "transcribing" | "extracting" | "summarizing" | "done";

export default function Dashboard() {
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
          if (!res.ok) throw new Error(`Server error: ${res.statusText}`);
          
          const data = await res.json();
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

      if (!res.ok) {
        throw new Error(`Server error: ${res.statusText}`);
      }
      
      const data = await res.json();
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
    { id: "transcribing", label: "Transcribing Audio" },
    { id: "extracting", label: "Extracting AI Entities" },
    { id: "summarizing", label: "Generating Intelligence" },
  ];

  return (
    <div className="w-full max-w-7xl mx-auto px-4 pb-20">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT PANEL: INPUT CONTROL */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-panel rounded-3xl p-6">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-brand-blue" />
              Configure Analysis
            </h2>

            <div className="flex bg-black/40 rounded-xl p-1 mb-6 border border-white/5">
              <button
                onClick={() => setMode("local")}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  mode === "local" ? "bg-muted text-white shadow-sm" : "text-muted-foreground hover:text-white"
                }`}
              >
                <Lock className="w-4 h-4" /> Local Edge
              </button>
              <button
                onClick={() => setMode("cloud")}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  mode === "cloud" ? "bg-brand-blue text-white shadow-md shadow-brand-blue/20" : "text-muted-foreground hover:text-white"
                }`}
              >
                <Cloud className="w-4 h-4" /> Cloud Fast
              </button>
            </div>

            <div className="space-y-3">
              {/* 🎙️ RECORD LIVE — Primary Action */}
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  disabled={step !== "idle" && step !== "done"}
                  className="w-full relative group bg-gradient-to-r from-red-500/10 to-red-500/5 hover:from-red-500/20 hover:to-red-500/10 border border-red-500/20 hover:border-red-500/30 rounded-2xl p-4 flex items-center gap-4 transition-all disabled:opacity-50"
                >
                  <div className="bg-red-500/20 p-3 rounded-full text-red-400">
                    <Radio className="w-6 h-6" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-red-300">Record Live Conversation</h3>
                    <p className="text-xs text-muted-foreground">Tap to start recording from microphone</p>
                  </div>
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="w-full relative group bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 rounded-2xl p-4 flex items-center gap-4 transition-all animate-pulse"
                >
                  <div className="relative">
                    <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-30" />
                    <div className="relative bg-red-500 p-3 rounded-full text-white">
                      <Square className="w-6 h-6" />
                    </div>
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-red-300">Stop & Analyze</h3>
                    <p className="text-xs text-red-400 font-mono">
                      🔴 Recording... {formatTime(recordingTime)}
                    </p>
                  </div>
                </button>
              )}

              {/* Demo Audio */}
              <button
                onClick={() => runAnalysis("demo")}
                disabled={(step !== "idle" && step !== "done") || isRecording}
                className="w-full relative group bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-4 flex items-center gap-4 transition-all disabled:opacity-50"
              >
                <div className="bg-brand-blue/20 p-3 rounded-full text-brand-blue">
                  <Mic className="w-6 h-6" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold">Run Demo Audio</h3>
                  <p className="text-xs text-muted-foreground">Arjun & Priya (Sample)</p>
                </div>
              </button>

              {/* Upload Audio */}
              <label
                className={`w-full relative group hover:bg-white/10 border border-white/10 rounded-2xl p-4 flex items-center gap-4 transition-all ${
                  (step !== "idle" && step !== "done") || isRecording ? "opacity-50 cursor-not-allowed bg-white/5" : "cursor-pointer bg-brand-teal/5"
                }`}
              >
                <input 
                   type="file" 
                   accept="audio/wav, audio/mpeg, audio/mp3, audio/m4a, audio/webm"
                   className="hidden" 
                   disabled={(step !== "idle" && step !== "done") || isRecording}
                   onChange={async (e) => {
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
                          if (!res.ok) throw new Error(`Server error: ${res.statusText}`);
                          
                          const data = await res.json();
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
                <div className="bg-brand-teal/20 p-3 rounded-full text-brand-teal">
                  <Upload className="w-6 h-6" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold">Upload Audio</h3>
                  <p className="text-xs text-muted-foreground">WAV, MP3, M4A up to 25MB</p>
                </div>
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

        {/* RIGHT PANEL: LIVE PROCESSING OR RESULTS */}
        <div className="lg:col-span-8">
          {step === "idle" && !result && (
             <div className="h-full min-h-[400px] glass-panel rounded-3xl flex flex-col items-center justify-center text-muted-foreground">
               <ShieldIcon className="w-16 h-16 mb-4 opacity-20" />
               <p>Waiting for audio input...</p>
             </div>
          )}

          {step !== "idle" && step !== "done" && (
            <div className="glass-panel rounded-3xl p-8 min-h-[400px] flex flex-col justify-center">
              <h2 className="text-2xl font-bold mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">
                Processing Conversation
              </h2>
              <div className="space-y-6 max-w-md mx-auto w-full">
                {stepsList.map((s, i) => {
                  const isActive = step === s.id;
                  const isPast = stepsList.findIndex((x) => x.id === step) > i;
                  return (
                    <div key={s.id} className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-500 ${
                        isActive ? "bg-brand-blue text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]" : 
                        isPast ? "bg-brand-teal text-white" : "bg-white/5 text-muted-foreground"
                      }`}>
                        {isActive ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                         isPast ? <span className="font-bold">✓</span> : 
                         <span className="text-sm">{i + 1}</span>}
                      </div>
                      <span className={`text-lg transition-colors duration-500 ${
                        isActive ? "text-white font-semibold" : 
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
    </div>
  );
}

const ShieldIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
  </svg>
);
