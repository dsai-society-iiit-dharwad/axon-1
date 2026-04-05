"use client";

import { motion } from "framer-motion";
import { MessageSquare } from "lucide-react";

export default function TranscriptView({ turns, entities }: { turns: any[]; entities: any[] }) {
  if (!turns || turns.length === 0) return null;

  // Simple hardcoded mapping for speakers
  const sColors = ["bg-brand-blue", "bg-brand-teal", "bg-purple-500", "bg-pink-500", "bg-orange-500"];
  
  const getSpeakerColor = (idx: number) => {
    return sColors[idx % sColors.length];
  };

  const speakers = Array.from(new Set(turns.map(t => t.speaker)));

  // Highlight entities in text
  const highlightText = (text: string) => {
    let highlightedText = text;
    entities.forEach(ent => {
        // Need to be careful to not break HTML with simple regex, but for a demo this is fast and visual.
        // A better approach would be to split the string into React nodes.
        const regex = new RegExp(`(${ent.text})`, "gi");
        highlightedText = highlightedText.replace(regex, `<span class="bg-white/20 text-white font-bold px-1 rounded mx-0.5 shadow-[0_0_10px_rgba(255,255,255,0.1)] border border-white/20">$1</span>`);
    });
    return <span dangerouslySetInnerHTML={{ __html: highlightedText }} />;
  };

  return (
    <div className="glass-card flex flex-col h-[500px] overflow-hidden relative">
      <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <h2 className="font-bold flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-brand-teal" />
          Raw Conversation
        </h2>
        <div className="flex gap-2">
          {speakers.map((spk: any, i: number) => (
            <div key={spk} className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 bg-black/40 border border-white/10 rounded-full">
               <div className={`w-2 h-2 rounded-full ${getSpeakerColor(i)}`} />
               {spk}
            </div>
          ))}
        </div>
      </div>

      <div className="p-6 overflow-y-auto flex-1 space-y-6 custom-scrollbar">
        {turns.map((turn: any, i: number) => {
          const spkIdx = speakers.indexOf(turn.speaker);
          const isMe = spkIdx === 0;

          return (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              key={i} 
              className={`flex flex-col max-w-[85%] ${isMe ? "ml-auto items-end" : "mr-auto items-start"}`}
            >
              <span className="text-xs text-muted-foreground mb-1 ml-1 font-medium">{turn.speaker} <span className="opacity-50">({(turn.start ?? turn.start_sec ?? 0).toFixed(1)}s)</span></span>
              <div 
                className={`p-4 rounded-3xl ${
                  isMe 
                  ? "bg-brand-blue/20 border border-brand-blue/30 text-brand-blue-50 rounded-tr-sm" 
                  : "bg-white/5 border border-white/10 text-white/90 rounded-tl-sm"
                }`}
              >
                <p className="text-[15px] leading-relaxed">
                  {highlightText(turn.text)}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
      
      {/* Scrollbar hide helper */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}} />
    </div>
  );
}
