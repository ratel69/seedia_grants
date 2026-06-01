import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "wouter";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreBadge, ActionBadge, StatusBadge, TrackBadge } from "@/components/ScoreBadge";
import { ExternalLink, Search, Database } from "lucide-react";
import type { Grant } from "@shared/schema";

const ACTIONS = ["all", "apply", "strong watch", "watch", "reject"];
const STATUSES = ["all", "new", "reviewed", "in preparation", "submitted", "won", "rejected"];
const TRACKS = ["all", "JST", "R&D", "EU_DIRECT"];

const TRACK_LABELS: Record<string, string> = {
  all:       "Wszystkie ścieżki",
  JST:       "🏛️ JST",
  "R&D":     "🔬 R&D",
  EU_DIRECT: "🇪🇺 EU Direct",
};

function DeadlineDays({ deadline }: { deadline?: string | null }) {
  if (!deadline) return <span className="text-muted-foreground text-xs">—</span>;
  const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000);
  const color = days <= 7 ? "text-red-400" : days <= 14 ? "text-amber-400" : days <= 30 ? "text-yellow-400" : "text-muted-foreground";
  return (
    <div>
      <div className="text-xs font-medium">{deadline}</div>
      <div className={`text-[10px] ${color}`}>
        {days <= 0 ? "po terminie" : `za ${days} dni`}
      </div>
    </div>
  );
}

export default function GrantsPage() {
  const [search, setSearch]   = useState("");
  const [action, setAction]   = useState("all");
  const [status, setStatus]   = useState("all");
  const [track, setTrack]     = useState("all");

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (action !== "all") params.set("action", action);
  if (status !== "all") params.set("status", status);
  if (track  !== "all") params.set("track", track);

  const { data: grants = [], isLoading } = useQuery<Grant[]>({
    queryKey: ["/api/grants", search, action, status, track],
    queryFn: () => apiRequest("GET", `/api/grants?${params}`).then(r => r.json()),
  });

  const seedMutation = useMutation({
    mutationFn: () => apiRequest("POST", "/api/seed").then(r => r.json()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["/api/grants"] }),
  });

  const applyCount      = grants.filter(g => g.recommendedAction === "apply").length;
  const strongWatchCount= grants.filter(g => g.recommendedAction === "strong watch").length;
  const jstCount        = grants.filter(g => (g as any).track === "JST").length;
  const rdCount         = grants.filter(g => (g as any).track === "R&D").length;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-xl font-bold">Radar Grantów</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {grants.length} grantów · {applyCount} apply · {strongWatchCount} strong watch
            {" · "}
            <span className="text-violet-400 font-medium">🏛️ {jstCount} JST</span>
            {" · "}
            <span className="text-cyan-400 font-medium">🔬 {rdCount} R&D</span>
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => seedMutation.mutate()}
          disabled={seedMutation.isPending}
          className="gap-2"
        >
          <Database className="w-3.5 h-3.5" />
          {seedMutation.isPending ? "Ładowanie..." : "Załaduj demo"}
        </Button>
      </div>

      {/* Track quick-filter pills */}
      <div className="flex gap-2 mb-4">
        {TRACKS.map(t => (
          <button
            key={t}
            onClick={() => setTrack(t)}
            className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
              track === t
                ? t === "JST"       ? "bg-violet-500/25 text-violet-300 border-violet-500/50"
                : t === "R&D"       ? "bg-cyan-500/25 text-cyan-300 border-cyan-500/50"
                : t === "EU_DIRECT" ? "bg-blue-500/25 text-blue-300 border-blue-500/50"
                :                     "bg-muted text-foreground border-border"
                : "bg-transparent text-muted-foreground border-border hover:border-muted-foreground"
            }`}
          >
            {TRACK_LABELS[t] ?? t}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <Input
            placeholder="Szukaj grantu..."
            className="pl-9 h-9 text-sm"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <Select value={action} onValueChange={setAction}>
          <SelectTrigger className="w-40 h-9 text-sm">
            <SelectValue placeholder="Rekomendacja" />
          </SelectTrigger>
          <SelectContent>
            {ACTIONS.map(a => (
              <SelectItem key={a} value={a}>{a === "all" ? "Wszystkie" : a.toUpperCase()}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40 h-9 text-sm">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {STATUSES.map(s => (
              <SelectItem key={s} value={s}>{s === "all" ? "Wszystkie statusy" : s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 border-b border-border">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Grant</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-24">Program</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-24">Track</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-28">Deadline</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-16">Score</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-32">Rekomendacja</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider w-28">Status</th>
              <th className="w-8"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {isLoading ? (
              Array(5).fill(0).map((_, i) => (
                <tr key={i}>
                  <td className="px-4 py-3"><Skeleton className="h-4 w-64" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-5 w-20" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-4 w-20" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-6 w-11 mx-auto" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-5 w-20" /></td>
                  <td className="px-4 py-3"><Skeleton className="h-5 w-16" /></td>
                  <td></td>
                </tr>
              ))
            ) : grants.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-muted-foreground text-sm">
                  Brak grantów spełniających kryteria.
                </td>
              </tr>
            ) : (
              grants.map(grant => (
                <tr key={grant.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3">
                    <Link href={`/grants/${grant.id}`}>
                      <a className="font-medium hover:text-primary transition-colors line-clamp-2">
                        {grant.grantName}
                      </a>
                    </Link>
                    {grant.seediaProductsFit && (
                      <div className="text-[10px] text-muted-foreground mt-0.5">
                        {(() => {
                          try { return JSON.parse(grant.seediaProductsFit as string).join(" · "); }
                          catch { return grant.seediaProductsFit; }
                        })()}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-muted-foreground">{grant.programme || "—"}</span>
                  </td>
                  <td className="px-4 py-3">
                    {(grant as any).track
                      ? <TrackBadge track={(grant as any).track} />
                      : <span className="text-muted-foreground text-xs">—</span>
                    }
                  </td>
                  <td className="px-4 py-3">
                    <DeadlineDays deadline={grant.deadline} />
                  </td>
                  <td className="px-4 py-3 text-center">
                    {grant.scoreTotal != null
                      ? <ScoreBadge score={grant.scoreTotal} />
                      : <span className="text-muted-foreground text-xs">—</span>
                    }
                  </td>
                  <td className="px-4 py-3">
                    {grant.recommendedAction
                      ? <ActionBadge action={grant.recommendedAction} />
                      : <span className="text-muted-foreground text-xs">—</span>
                    }
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={grant.status || "new"} />
                  </td>
                  <td className="px-4 py-3">
                    {grant.url && (
                      <a href={grant.url} target="_blank" rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors">
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
