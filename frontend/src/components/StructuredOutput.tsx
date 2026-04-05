"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Braces, Copy, Check, Download, ArrowRight } from "lucide-react";

export default function StructuredOutput({ result }: { result: any }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  // Build the final structured JSON — ONLY the intelligence output
  // Raw transcript is shown separately in the TranscriptView component
  const structuredReport = {
    meta: {
      conversation_id: result.conv_id,
      language_detected: result.language,
      speakers_identified: result.speaker_count,
      duration_seconds: parseFloat(result.duration?.toFixed(1)),
      is_financial: result.is_financial,
      financial_confidence: result.fin_score,
      processing_time: result.pipeline_time + "s",
      backend: result.backend,
    },
    extracted_entities: (result.entities || []).map((e: any) => ({
      original_text: e.text,
      type: e.short_label || e.label,
      normalized_value: e.normalized,
    })),
    financial_intelligence: {
      commitments: result.summary?.commitments || [],
      pending_decisions: result.summary?.pending_decisions || [],
      financial_snapshot: result.summary?.financial_snapshot || {},
      speaker_sentiments: result.summary?.speaker_sentiments || [],
      risk_assessment: {
        score: result.summary?.risk_score ?? null,
        label: result.summary?.risk_label ?? "N/A",
        reasoning: result.summary?.risk_reasoning ?? "",
      },
    },
  };

  const jsonString = JSON.stringify(structuredReport, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `armor_report_${result.conv_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="glass-card overflow-hidden"
    >
      {/* Header */}
      <div className="p-5 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="bg-brand-blue/20 p-2 rounded-lg">
            <Braces className="w-5 h-5 text-brand-blue" />
          </div>
          <div>
            <h2 className="font-bold text-lg">Structured JSON Output</h2>
            <p className="text-xs text-muted-foreground">
              Unstructured conversation → Structured financial intelligence
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-all"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied!" : "Copy"}
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-brand-blue/20 hover:bg-brand-blue/30 text-brand-blue border border-brand-blue/20 rounded-lg transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            Export .json
          </button>
        </div>
      </div>

      {/* Transformation banner */}
      <div className="px-5 py-3 bg-gradient-to-r from-brand-blue/10 to-brand-teal/10 border-b border-white/5 flex items-center gap-3 text-sm">
        <span className="bg-white/10 px-2.5 py-0.5 rounded-full text-xs font-semibold text-white/60">INPUT</span>
        <span className="text-muted-foreground truncate max-w-[200px]">
          Raw multilingual conversation ({result.speaker_count} speakers, {result.language})
        </span>
        <ArrowRight className="w-4 h-4 text-brand-teal shrink-0" />
        <span className="bg-brand-teal/20 px-2.5 py-0.5 rounded-full text-xs font-semibold text-brand-teal">OUTPUT</span>
        <span className="text-white/80 font-medium">Structured Financial Report</span>
      </div>

      {/* JSON Viewer */}
      <div className="p-5 max-h-[600px] overflow-auto custom-scrollbar">
        <pre className="text-sm leading-relaxed font-mono">
          <JSONHighlighter json={structuredReport} />
        </pre>
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
      `}} />
    </motion.div>
  );
}

// Syntax highlighted JSON renderer
function JSONHighlighter({ json, indent = 0 }: { json: any; indent?: number }) {
  const pad = "  ".repeat(indent);
  
  if (json === null) return <span className="text-orange-400">null</span>;
  if (typeof json === "boolean") return <span className="text-orange-400">{json.toString()}</span>;
  if (typeof json === "number") return <span className="text-brand-teal">{json}</span>;
  if (typeof json === "string") return <span className="text-green-400">&quot;{json}&quot;</span>;
  
  if (Array.isArray(json)) {
    if (json.length === 0) return <span className="text-white/40">{"[]"}</span>;
    return (
      <>
        <span className="text-white/60">{"["}</span>{"\n"}
        {json.map((item, i) => (
          <span key={i}>
            {pad}{"  "}<JSONHighlighter json={item} indent={indent + 1} />
            {i < json.length - 1 ? <span className="text-white/40">,</span> : null}{"\n"}
          </span>
        ))}
        {pad}<span className="text-white/60">{"]"}</span>
      </>
    );
  }

  if (typeof json === "object") {
    const keys = Object.keys(json);
    if (keys.length === 0) return <span className="text-white/40">{"{}"}</span>;
    return (
      <>
        <span className="text-white/60">{"{"}</span>{"\n"}
        {keys.map((key, i) => (
          <span key={key}>
            {pad}{"  "}<span className="text-brand-blue">&quot;{key}&quot;</span>
            <span className="text-white/40">: </span>
            <JSONHighlighter json={json[key]} indent={indent + 1} />
            {i < keys.length - 1 ? <span className="text-white/40">,</span> : null}{"\n"}
          </span>
        ))}
        {pad}<span className="text-white/60">{"}"}</span>
      </>
    );
  }

  return <span>{String(json)}</span>;
}
