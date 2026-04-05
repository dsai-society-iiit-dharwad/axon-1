import { motion } from "framer-motion";
import { Wallet, PieChart, Clock, Hash } from "lucide-react";

export default function InsightsPanel({ entities }: { entities: any[] }) {
  if (!entities || entities.length === 0) return null;

  const amounts = entities.filter(e => e.short_label === "AMOUNT");
  const instruments = entities.filter(e => e.short_label === "INSTRUMENT");
  const timelines = entities.filter(e => e.short_label === "TIMELINE");

  const Card = ({ title, icon: Icon, items, colorClass }: any) => (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-colors">
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg ${colorClass}`}>
          <Icon className="w-5 h-5" />
        </div>
        <h3 className="font-semibold text-white/90">{title}</h3>
      </div>
      {items.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {items.map((e: any, i: number) => (
            <motion.span 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.05 }}
              key={i} 
              className="px-3 py-1 bg-black/40 border border-white/10 rounded-full text-sm text-white/80 select-all"
            >
              {e.normalized !== e.text ? (
                <span className="font-bold text-white">{e.normalized} <span className="text-xs text-muted-foreground font-normal ml-1">({e.text})</span></span>
              ) : (
                <span className="font-bold text-white">{e.normalized}</span>
              )}
            </motion.span>
          ))}
        </div>
      ) : (
        <span className="text-sm text-muted-foreground italic">None detected</span>
      )}
    </div>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card 
        title="Amounts" 
        icon={Wallet} 
        items={amounts} 
        colorClass="bg-green-500/20 text-green-400" 
      />
      <Card 
        title="Instruments" 
        icon={PieChart} 
        items={instruments} 
        colorClass="bg-brand-blue/20 text-brand-blue" 
      />
      <Card 
        title="Timelines" 
        icon={Clock} 
        items={timelines} 
        colorClass="bg-purple-500/20 text-purple-400" 
      />
    </div>
  );
}
