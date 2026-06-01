import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreBadge, ActionBadge, StatusBadge } from "@/components/ScoreBadge";
import { ArrowLeft, ExternalLink, FileText, Calendar, Euro, Users, MapPin, Lightbulb, AlertTriangle, ChevronRight } from "lucide-react";
import type { Grant, GrantFiche } from "@shared/schema";

function InfoRow({ label, value }: { label: string; value?: string | number | boolean | null }) {
  if (value == null || value === "") return null;
  return (
    <div className="flex gap-3">
      <dt className="text-xs text-muted-foreground w-40 shrink-0 pt-0.5">{label}</dt>
      <dd className="text-sm font-medium">{String(value)}</dd>
    </div>
  );
}

function FitBar({ label, value }: { label: string; value?: number | null }) {
  if (value == null) return null;
  const pct = (value / 5) * 100;
  const color = value >= 4 ? "bg-emerald-500" : value >= 3 ? "bg-amber-500" : "bg-blue-500";
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-muted-foreground w-40 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-muted-foreground w-8 text-right">{value}/5</span>
    </div>
  );
}

const STATUSES = ["new", "reviewed", "in preparation", "submitted", "won", "rejected", "archived"];

export default function GrantDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: grant, isLoading } = useQuery<Grant>({
    queryKey: ["/api/grants", id],
    queryFn: () => apiRequest("GET", `/api/grants/${id}`).then(r => r.json()),
  });

  const { data: fiche } = useQuery<GrantFiche>({
    queryKey: ["/api/grants", id, "fiche"],
    queryFn: () => apiRequest("GET", `/api/grants/${id}/fiche`).then(r => r.json()),
    retry: false,
  });

  const statusMutation = useMutation({
    mutationFn: (status: string) =>
      apiRequest("PATCH", `/api/grants/${id}/status`, { status }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/grants", id] });
      queryClient.invalidateQueries({ queryKey: ["/api/grants"] });
    },
  });

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-6 w-64" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!grant) return <div className="p-6 text-muted-foreground">Grant nie znaleziony.</div>;

  const products = (() => {
    try { return JSON.parse(grant.seediaProductsFit as string); } catch { return []; }
  })();

  const applicants = (() => {
    try { return JSON.parse(grant.eligibleApplicants as string); } catch { return []; }
  })();

  const countries = (() => {
    try { return JSON.parse(grant.eligibleCountries as string); } catch { return []; }
  })();

  const budgetStr = grant.fundingAmountMax
    ? `${grant.fundingAmountMax.toLocaleString("pl-PL")} EUR`
    : "nieznany";

  return (
    <div className="p-6 max-w-4xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-5">
        <Link href="/grants">
          <a className="hover:text-foreground transition-colors">Granty</a>
        </Link>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-foreground truncate max-w-xs">{grant.grantName}</span>
      </div>

      {/* Title row */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap mb-2">
            {grant.scoreTotal != null && <ScoreBadge score={grant.scoreTotal} />}
            {grant.recommendedAction && <ActionBadge action={grant.recommendedAction} />}
            <StatusBadge status={grant.status || "new"} />
          </div>
          <h1 className="text-xl font-bold leading-tight">{grant.grantName}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {grant.programme} · {grant.sourceName}
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          {grant.url && (
            <Button variant="outline" size="sm" asChild>
              <a href={grant.url} target="_blank" rel="noopener noreferrer" data-testid="link-external">
                <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                Otwórz
              </a>
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left column */}
        <div className="col-span-2 space-y-6">

          {/* Key facts */}
          <section className="rounded-lg border border-border p-4 space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Kluczowe dane</h2>
            <dl className="space-y-2">
              <InfoRow label="Deadline" value={grant.deadline} />
              <InfoRow label="Otwarcie naboru" value={grant.openingDate} />
              <InfoRow label="Budżet max" value={budgetStr} />
              <InfoRow label="Dofinansowanie" value={grant.fundingRate ? `${grant.fundingRate}%` : null} />
              <InfoRow label="Wkład własny" value={grant.ownContributionPct ? `${grant.ownContributionPct}%` : grant.ownContributionRequired === false ? "nie wymagany" : null} />
              <InfoRow label="Typ projektu" value={grant.projectType} />
              <InfoRow label="Ryzyko" value={grant.riskLevel} />
            </dl>
          </section>

          {/* Kwalifikowalność */}
          <section className="rounded-lg border border-border p-4 space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Kwalifikowalność</h2>
            {applicants.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {applicants.map((a: string) => (
                  <span key={a} className="text-xs bg-muted px-2 py-0.5 rounded-full text-muted-foreground">{a}</span>
                ))}
              </div>
            )}
            {countries.length > 0 && (
              <div className="flex gap-1.5 flex-wrap mt-2">
                <span className="text-xs text-muted-foreground">Kraje:</span>
                {countries.map((c: string) => (
                  <span key={c} className="text-xs font-medium">{c}</span>
                ))}
              </div>
            )}
          </section>

          {/* Produkty SEEDiA */}
          {products.length > 0 && (
            <section className="rounded-lg border border-border p-4 space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Produkty SEEDiA</h2>
              <div className="flex gap-2 flex-wrap">
                {products.map((p: string) => (
                  <span key={p} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full border border-primary/20 font-medium">
                    {p}
                  </span>
                ))}
              </div>
            </section>
          )}

          {/* Scoring breakdown */}
          <section className="rounded-lg border border-border p-4 space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Dopasowanie tematyczne</h2>
            <div className="space-y-2">
              <FitBar label="Smart city" value={grant.fitSmartCity} />
              <FitBar label="Mikromobilność" value={grant.fitMicromobility} />
              <FitBar label="Energia odnawialna" value={grant.fitRenewableEnergy} />
              <FitBar label="Dane / AI" value={grant.fitDataAi} />
              <FitBar label="Infrastruktura miejska" value={grant.fitUrbanInfrastructure} />
              <FitBar label="Resilience" value={grant.fitResilience} />
            </div>
            {grant.scoreReasoning && (
              <p className="text-sm text-muted-foreground mt-3 border-t border-border pt-3">
                {grant.scoreReasoning}
              </p>
            )}
          </section>

          {/* Koncepcja projektu */}
          {grant.suggestedConcept && (
            <section className="rounded-lg border border-border p-4 space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Lightbulb className="w-3.5 h-3.5" /> Sugerowana koncepcja projektu
              </h2>
              <p className="text-sm leading-relaxed">{grant.suggestedConcept}</p>
            </section>
          )}

          {/* Ryzyka */}
          {grant.keyRisks && (
            <section className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-amber-500 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5" /> Ryzyka
              </h2>
              <p className="text-sm text-muted-foreground">{grant.keyRisks}</p>
            </section>
          )}

          {/* Fiszka */}
          {fiche && (
            <section className="rounded-lg border border-border p-4 space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <FileText className="w-3.5 h-3.5" /> Fiszka grantu
              </h2>
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono leading-relaxed bg-muted/30 rounded p-3 overflow-auto max-h-96">
                {fiche.contentMd}
              </pre>
            </section>
          )}
        </div>

        {/* Right sidebar */}
        <div className="space-y-4">
          {/* Status change */}
          <div className="rounded-lg border border-border p-4 space-y-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Status</h2>
            <Select
              value={grant.status || "new"}
              onValueChange={val => statusMutation.mutate(val)}
              disabled={statusMutation.isPending}
            >
              <SelectTrigger className="h-9 text-sm" data-testid="select-grant-status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUSES.map(s => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Next action */}
          {grant.nextAction && (
            <div className="rounded-lg border border-primary/20 bg-primary/5 p-4 space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-primary">Następny krok</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">{grant.nextAction}</p>
            </div>
          )}

          {/* Quick score */}
          {grant.scoreTotal != null && (
            <div className="rounded-lg border border-border p-4 text-center">
              <div className="text-3xl font-bold tabular-nums">{grant.scoreTotal}</div>
              <div className="text-xs text-muted-foreground mt-1">/ 100 punktów</div>
              {grant.recommendedAction && (
                <div className="mt-2">
                  <ActionBadge action={grant.recommendedAction} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
