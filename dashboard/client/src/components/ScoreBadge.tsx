import { cn } from "@/lib/utils";

interface Props {
  score: number;
  className?: string;
}

export function ScoreBadge({ score, className }: Props) {
  const color =
    score >= 80 ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" :
    score >= 65 ? "bg-amber-500/15 text-amber-400 border-amber-500/30" :
    score >= 45 ? "bg-blue-500/15 text-blue-400 border-blue-500/30" :
    "bg-red-500/15 text-red-400 border-red-500/30";

  return (
    <span className={cn(
      "inline-flex items-center justify-center w-11 h-6 rounded text-xs font-bold border tabular-nums",
      color, className
    )} data-testid={`score-badge-${score}`}>
      {score}
    </span>
  );
}

export function ActionBadge({ action }: { action: string }) {
  const styles: Record<string, string> = {
    "apply":        "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    "strong watch": "bg-amber-500/15 text-amber-400 border-amber-500/30",
    "watch":        "bg-blue-500/15 text-blue-400 border-blue-500/30",
    "reject":       "bg-red-500/15 text-red-400 border-red-500/30",
  };
  const labels: Record<string, string> = {
    "apply":        "APPLY",
    "strong watch": "STRONG WATCH",
    "watch":        "WATCH",
    "reject":       "REJECT",
  };
  return (
    <span className={cn(
      "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wide",
      styles[action] ?? "bg-muted text-muted-foreground border-border"
    )}>
      {labels[action] ?? action}
    </span>
  );
}

export function TrackBadge({ track }: { track: string }) {
  const styles: Record<string, string> = {
    "JST":       "bg-violet-500/15 text-violet-400 border-violet-500/30",
    "R&D":       "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
    "EU_DIRECT": "bg-blue-500/15 text-blue-400 border-blue-500/30",
  };
  const labels: Record<string, string> = {
    "JST":       "🏛️ JST",
    "R&D":       "🔬 R&D",
    "EU_DIRECT": "🇪🇺 EU Direct",
  };
  return (
    <span className={cn(
      "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border",
      styles[track] ?? "bg-muted text-muted-foreground border-border"
    )}>
      {labels[track] ?? track}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    "new":            "bg-slate-500/15 text-slate-400 border-slate-500/30",
    "reviewed":       "bg-violet-500/15 text-violet-400 border-violet-500/30",
    "in preparation": "bg-amber-500/15 text-amber-400 border-amber-500/30",
    "submitted":      "bg-blue-500/15 text-blue-400 border-blue-500/30",
    "won":            "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    "rejected":       "bg-red-500/15 text-red-400 border-red-500/30",
    "archived":       "bg-muted text-muted-foreground border-border",
  };
  return (
    <span className={cn(
      "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border capitalize",
      styles[status] ?? "bg-muted text-muted-foreground border-border"
    )}>
      {status}
    </span>
  );
}
