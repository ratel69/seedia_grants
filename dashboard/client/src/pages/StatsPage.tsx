import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Skeleton } from "@/components/ui/skeleton";
import { Rocket, Eye, Clock, TrendingUp, CheckCircle2, XCircle, BarChart3 } from "lucide-react";

interface Stats {
  total: number;
  apply: number;
  strongWatch: number;
  watch: number;
  rejected: number;
  avgScore: number;
  withDeadline30d: number;
}

function StatCard({ label, value, icon: Icon, color }: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border p-4" data-testid={`stat-card-${label}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-muted-foreground">{label}</span>
        <div className={`w-7 h-7 rounded-md flex items-center justify-center ${color}`}>
          <Icon className="w-3.5 h-3.5" />
        </div>
      </div>
      <div className="text-2xl font-bold tabular-nums">{value}</div>
    </div>
  );
}

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ["/api/grants/stats"],
    queryFn: () => apiRequest("GET", "/api/grants/stats").then(r => r.json()),
  });

  if (isLoading || !stats) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-bold mb-6">Statystyki</h1>
        <div className="grid grid-cols-4 gap-4">
          {Array(7).fill(0).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)}
        </div>
      </div>
    );
  }

  const watchTotal = stats.strongWatch + stats.watch;

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-2">Statystyki</h1>
      <p className="text-sm text-muted-foreground mb-6">Podsumowanie bazy grantów SEEDiA</p>

      {/* KPI grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Wszystkich grantów" value={stats.total} icon={BarChart3} color="bg-muted text-muted-foreground" />
        <StatCard label="APPLY" value={stats.apply} icon={Rocket} color="bg-emerald-500/15 text-emerald-400" />
        <StatCard label="WATCH / STRONG WATCH" value={watchTotal} icon={Eye} color="bg-amber-500/15 text-amber-400" />
        <StatCard label="Deadline w 30 dni" value={stats.withDeadline30d} icon={Clock} color="bg-red-500/15 text-red-400" />
        <StatCard label="Śr. wynik dopasowania" value={`${stats.avgScore}/100`} icon={TrendingUp} color="bg-primary/15 text-primary" />
        <StatCard label="Odrzucone" value={stats.rejected} icon={XCircle} color="bg-muted text-muted-foreground" />
      </div>

      {/* Decision breakdown */}
      <div className="rounded-lg border border-border p-5">
        <h2 className="text-sm font-semibold mb-4">Rozkład rekomendacji</h2>
        <div className="space-y-3">
          {[
            { label: "APPLY", value: stats.apply, color: "bg-emerald-500", max: stats.total },
            { label: "STRONG WATCH", value: stats.strongWatch, color: "bg-amber-500", max: stats.total },
            { label: "WATCH", value: stats.watch, color: "bg-blue-500", max: stats.total },
            { label: "REJECT", value: stats.rejected, color: "bg-red-500", max: stats.total },
          ].map(({ label, value, color, max }) => (
            <div key={label} className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground w-28">{label}</span>
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${color}`}
                  style={{ width: max > 0 ? `${(value / max) * 100}%` : "0%" }}
                />
              </div>
              <span className="text-xs font-mono text-muted-foreground w-6 text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
