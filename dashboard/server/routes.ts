import type { Express } from "express";
import { createServer } from "http";
import { storage } from "./storage";
import { insertGrantSchema } from "@shared/schema";
import { z } from "zod";
import { randomUUID } from "crypto";

export function registerRoutes(httpServer: ReturnType<typeof createServer>, app: Express) {

  // ─── GRANTS ────────────────────────────────────────────────────────────────

  // GET /api/grants — list with filters
  app.get("/api/grants", (req, res) => {
    try {
      const { status, action, search, minScore } = req.query;
      const grants = storage.getGrants({
        status: status as string,
        recommendedAction: action as string,
        search: search as string,
        minScore: minScore ? parseInt(minScore as string) : undefined,
      });
      res.json(grants);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // GET /api/grants/stats — dashboard stats
  app.get("/api/grants/stats", (req, res) => {
    try {
      res.json(storage.getStats());
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // GET /api/grants/:id — single grant
  app.get("/api/grants/:id", (req, res) => {
    try {
      const grant = storage.getGrantById(req.params.id);
      if (!grant) return res.status(404).json({ error: "Not found" });
      res.json(grant);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // POST /api/grants — create/upsert grant (used by scanner)
  app.post("/api/grants", (req, res) => {
    try {
      const data = insertGrantSchema.parse(req.body);
      const grant = storage.upsertGrant(data);
      res.json(grant);
    } catch (e: any) {
      res.status(400).json({ error: e.message });
    }
  });

  // PATCH /api/grants/:id/status — update status
  app.patch("/api/grants/:id/status", (req, res) => {
    try {
      const { status, owner } = z.object({
        status: z.string(),
        owner: z.string().optional(),
      }).parse(req.body);
      const updated = storage.updateGrantStatus(req.params.id, status, owner);
      res.json(updated);
    } catch (e: any) {
      res.status(400).json({ error: e.message });
    }
  });

  // ─── FICHES ────────────────────────────────────────────────────────────────

  // GET /api/grants/:id/fiche — get fiche for grant
  app.get("/api/grants/:id/fiche", (req, res) => {
    try {
      const fiche = storage.getFicheByGrantId(req.params.id);
      if (!fiche) return res.status(404).json({ error: "Fiche not found" });
      res.json(fiche);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // POST /api/grants/:id/fiche — save fiche
  app.post("/api/grants/:id/fiche", (req, res) => {
    try {
      const { content_md } = z.object({ content_md: z.string() }).parse(req.body);
      const fiche = storage.upsertFiche({
        id: randomUUID(),
        grantId: req.params.id,
        contentMd: content_md,
      });
      res.json(fiche);
    } catch (e: any) {
      res.status(400).json({ error: e.message });
    }
  });

  // ─── SCAN LOGS ─────────────────────────────────────────────────────────────

  // GET /api/scan-logs — last scan logs
  app.get("/api/scan-logs", (req, res) => {
    try {
      const logs = storage.getScanLogs(20);
      res.json(logs);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ─── SEED DEMO DATA (DEV ONLY) ─────────────────────────────────────────────
  app.post("/api/seed", (req, res) => {
    try {
      const demo = [
        {
          id: randomUUID(),
          grantName: "EIT Urban Mobility — Strategic Innovation Open Call 2026",
          sourceName: "EIT Urban Mobility",
          programme: "EIT",
          url: "https://www.eiturbanmobility.eu/join-us/call-for-proposals/strategic-innovation-2026",
          deadline: "2026-09-15",
          openingDate: "2026-05-01",
          fundingAmountMax: 2000000,
          fundingRate: 70,
          ownContributionRequired: true,
          ownContributionPct: 30,
          eligibleApplicants: JSON.stringify(["MŚP", "konsorcjum", "startup"]),
          eligibleCountries: JSON.stringify(["UE", "associated countries"]),
          projectType: "pilotaż",
          seediaProductsFit: JSON.stringify(["jCharge", "incity.io", "UrbMap"]),
          fitSmartCity: 5,
          fitMicromobility: 5,
          fitRenewableEnergy: 3,
          fitDataAi: 4,
          fitUrbanInfrastructure: 5,
          fitResilience: 3,
          scoreTotal: 88,
          scoreReasoning: "Doskonałe dopasowanie produktów SEEDiA do zakresu naboru. EIT wspiera MŚP technologiczne w UE. Pilotaże mobilności miejskiej to core business SEEDiA.",
          riskLevel: "niski",
          keyRisks: "Konieczność partnera z europejskiego miasta. Wymagany wkład własny 30%.",
          recommendedAction: "apply",
          suggestedConcept: "Projekt pilotażowy integracji stacji ładowania jCharge z platformą incity.io w 3 europejskich miastach. Celem jest demonstracja interoperacyjności infrastruktury ładowania z systemem zarządzania danymi miejskimi. Pilotaż obejmie 50 urządzeń jCharge + moduł analityczny UrbMap. Partnerzy: 2 miasta z UE + operator mikromobilności.",
          nextAction: "Skontaktować się z EIT w sprawie partnerstw. Przygotować letter of intent do 15.07.2026.",
          status: "new",
          aiExtracted: true,
        },
        {
          id: randomUUID(),
          grantName: "PARP FENG 1.1 — Innowacje dla MŚP — nabór Q3 2026",
          sourceName: "PARP — harmonogram naborów",
          programme: "PARP",
          url: "https://www.parp.gov.pl/feng-1-1-innowacje-msP-2026",
          deadline: "2026-08-30",
          openingDate: "2026-07-01",
          fundingAmountMax: 1500000,
          fundingRate: 80,
          ownContributionRequired: true,
          ownContributionPct: 20,
          eligibleApplicants: JSON.stringify(["MŚP", "spółka polska"]),
          eligibleCountries: JSON.stringify(["PL"]),
          projectType: "B+R",
          seediaProductsFit: JSON.stringify(["AI camera", "incity.io", "e-paper"]),
          fitSmartCity: 4,
          fitMicromobility: 3,
          fitRenewableEnergy: 3,
          fitDataAi: 5,
          fitUrbanInfrastructure: 4,
          fitResilience: 2,
          scoreTotal: 74,
          scoreReasoning: "Dobry nabór dla projektu B+R SEEDiA w obszarze AI i edge computing. SEEDiA w pełni kwalifikowalna jako polskie MŚP. Finansowanie B+R do 80% kosztów.",
          riskLevel: "średni",
          keyRisks: "Konieczność wykazania innowacyjności na poziomie kraju. Wysokie wymogi raportowania.",
          recommendedAction: "strong watch",
          suggestedConcept: "Projekt B+R na opracowanie zaawansowanego modułu AI do analizy ruchu miejskiego opartego na kamerze AI SEEDiA. Celem jest stworzenie edge AI przetwarzającego dane lokalnie bez przesyłu do chmury.",
          nextAction: "Złożyć wstępny wniosek EOI do 15.07.2026. Przygotować dokumentację innowacyjności.",
          status: "reviewed",
          aiExtracted: true,
        },
        {
          id: randomUUID(),
          grantName: "Horizon Europe Cluster 5 — Smart Cities Mission Call 2026",
          sourceName: "EU Funding & Tenders Portal",
          programme: "Horizon Europe",
          url: "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals/horizon-cluster5-smart-cities-2026",
          deadline: "2026-11-20",
          openingDate: "2026-06-01",
          fundingAmountMax: 8000000,
          fundingRate: 100,
          ownContributionRequired: false,
          eligibleApplicants: JSON.stringify(["konsorcjum", "MŚP", "uczelnia", "miasto"]),
          eligibleCountries: JSON.stringify(["UE", "associated countries"]),
          projectType: "demonstrator",
          seediaProductsFit: JSON.stringify(["solar shelter", "AI camera", "incity.io", "e-paper", "jCharge"]),
          fitSmartCity: 5,
          fitMicromobility: 4,
          fitRenewableEnergy: 5,
          fitDataAi: 4,
          fitUrbanInfrastructure: 5,
          fitResilience: 4,
          scoreTotal: 82,
          scoreReasoning: "Bardzo dobre dopasowanie tematyczne. 100% dofinansowania eliminuje barierę wkładu własnego. Wymaga silnego konsorcjum z miastem jako liderem.",
          riskLevel: "wysoki",
          keyRisks: "Konieczność konsorcjum 5+ partnerów. Skomplikowana aplikacja. Wymagane miasto jako lider projektu.",
          recommendedAction: "apply",
          suggestedConcept: "Demonstrator integracji odnawialnej infrastruktury miejskiej SEEDiA w 3 miastach misji smart city. Projekt obejmie solar sheltery, stacje jCharge, kamery AI i platformę incity.io jako zintegrowany ekosystem smart city.",
          nextAction: "Zidentyfikować lidera miejskiego (np. Warszawa, Gdańsk, Poznań). Skontaktować się z EEN w sprawie partnerstw. Deadline aplikacji: 20.11.2026.",
          status: "new",
          aiExtracted: true,
        },
        {
          id: randomUUID(),
          grantName: "NCBR Szybka Ścieżka — Technologie Energetyczne 2026",
          sourceName: "NCBR — harmonogram konkursów",
          programme: "NCBR",
          url: "https://www.gov.pl/web/ncbr/szybka-sciezka-energia-2026",
          deadline: "2026-07-15",
          fundingAmountMax: 5000000,
          fundingRate: 80,
          ownContributionRequired: true,
          ownContributionPct: 20,
          eligibleApplicants: JSON.stringify(["MŚP", "duże przedsiębiorstwo", "konsorcjum"]),
          eligibleCountries: JSON.stringify(["PL"]),
          projectType: "B+R",
          seediaProductsFit: JSON.stringify(["solar shelter", "jCharge"]),
          fitSmartCity: 3,
          fitMicromobility: 4,
          fitRenewableEnergy: 5,
          fitDataAi: 2,
          fitUrbanInfrastructure: 3,
          fitResilience: 3,
          scoreTotal: 68,
          scoreReasoning: "Dobre dopasowanie dla projektu B+R w obszarze solarnym. Wysoki budżet. Krótki deadline wymaga szybkiej decyzji.",
          riskLevel: "średni",
          keyRisks: "Deadline za 47 dni. Wymaga gotowej dokumentacji technicznej B+R.",
          recommendedAction: "strong watch",
          suggestedConcept: "Projekt B+R nad nową generacją ogniw fotowoltaicznych zintegrowanych z infrastrukturą miejską SEEDiA (solar shelter 2.0 z wyższą sprawnością i zasobnikiem energii).",
          nextAction: "Ocenić gotowość dokumentacji B+R do 10.06.2026. Decyzja: aplikować czy watch.",
          status: "new",
          aiExtracted: true,
        },
        {
          id: randomUUID(),
          grantName: "LIFE Climate Action — Resilient Urban Infrastructure 2026",
          sourceName: "LIFE / CINEA",
          programme: "LIFE",
          url: "https://cinea.ec.europa.eu/life-climate-resilient-urban-2026",
          deadline: "2026-10-05",
          fundingAmountMax: 3000000,
          fundingRate: 60,
          ownContributionRequired: true,
          ownContributionPct: 40,
          eligibleApplicants: JSON.stringify(["NGO", "MŚP", "miasto", "fundacja"]),
          eligibleCountries: JSON.stringify(["UE"]),
          projectType: "demonstrator",
          seediaProductsFit: JSON.stringify(["solar shelter", "infokiosk", "e-paper"]),
          fitSmartCity: 4,
          fitMicromobility: 2,
          fitRenewableEnergy: 5,
          fitDataAi: 2,
          fitUrbanInfrastructure: 5,
          fitResilience: 5,
          scoreTotal: 65,
          scoreReasoning: "Dobre dopasowanie w obszarze resilience i energii solarnej. Wkład własny 40% jest wysoki ale możliwy przy partnerze miejskim.",
          riskLevel: "średni",
          keyRisks: "Wysoki wkład własny (40%). Preferowane NGO i miasta jako beneficjenci.",
          recommendedAction: "watch",
          suggestedConcept: "Demonstrator odpornej infrastruktury miejskiej działającej autonomicznie przy awariach sieci: solar sheltery, kryzysowe infokioski, e-paper systemy informacji.",
          nextAction: "Zidentyfikować partnera NGO lub miejskiego jako lidera. Ocenić zdolność wkładu własnego 40%.",
          status: "new",
          aiExtracted: true,
        },
      ];

      for (const g of demo) {
        storage.upsertGrant(g as any);
      }
      res.json({ inserted: demo.length });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });
}
