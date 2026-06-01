import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// ─── GRANTS ─────────────────────────────────────────────────────────────────
export const grants = sqliteTable("grants", {
  id:                       text("id").primaryKey(),
  grantName:                text("grant_name").notNull(),
  sourceName:               text("source_name"),
  programme:                text("programme"),
  url:                      text("url").unique(),
  openingDate:              text("opening_date"),
  deadline:                 text("deadline"),
  fundingAmountMin:         integer("funding_amount_min"),
  fundingAmountMax:         integer("funding_amount_max"),
  fundingRate:              integer("funding_rate"),
  ownContributionRequired:  integer("own_contribution_required", { mode: "boolean" }),
  ownContributionPct:       integer("own_contribution_pct"),
  eligibleApplicants:       text("eligible_applicants"),   // JSON array
  eligibleCountries:        text("eligible_countries"),    // JSON array
  projectType:              text("project_type"),
  seediaProductsFit:        text("seedia_products_fit"),   // JSON array
  fitSmartCity:             integer("fit_smart_city"),
  fitMicromobility:         integer("fit_micromobility"),
  fitRenewableEnergy:       integer("fit_renewable_energy"),
  fitDataAi:                integer("fit_data_ai"),
  fitUrbanInfrastructure:   integer("fit_urban_infrastructure"),
  fitResilience:            integer("fit_resilience"),
  scoreTotal:               integer("score_total"),
  scoreReasoning:           text("score_reasoning"),
  riskLevel:                text("risk_level"),
  keyRisks:                 text("key_risks"),
  recommendedAction:        text("recommended_action"),
  suggestedConcept:         text("suggested_concept"),
  nextAction:               text("next_action"),
  status:                   text("status").default("new"),
  owner:                    text("owner"),
  aiExtracted:              integer("ai_extracted", { mode: "boolean" }).default(false),
  aiExtractedAt:            text("ai_extracted_at"),
  alertSent:                integer("alert_sent", { mode: "boolean" }).default(false),
  createdAt:                text("created_at").default(new Date().toISOString()),
  updatedAt:                text("updated_at").default(new Date().toISOString()),
});

export const insertGrantSchema = createInsertSchema(grants).omit({
  createdAt: true,
  updatedAt: true,
});
export type InsertGrant = z.infer<typeof insertGrantSchema>;
export type Grant = typeof grants.$inferSelect;

// ─── GRANT FICHES ────────────────────────────────────────────────────────────
export const grantFiches = sqliteTable("grant_fiches", {
  id:          text("id").primaryKey(),
  grantId:     text("grant_id").notNull(),
  contentMd:   text("content_md").notNull(),
  generatedAt: text("generated_at").default(new Date().toISOString()),
});

export const insertFicheSchema = createInsertSchema(grantFiches).omit({ generatedAt: true });
export type InsertFiche = z.infer<typeof insertFicheSchema>;
export type GrantFiche = typeof grantFiches.$inferSelect;

// ─── SCAN LOGS ───────────────────────────────────────────────────────────────
export const scanLogs = sqliteTable("scan_logs", {
  id:            text("id").primaryKey(),
  sourceName:    text("source_name"),
  scannedAt:     text("scanned_at").default(new Date().toISOString()),
  newGrants:     integer("new_grants").default(0),
  updatedGrants: integer("updated_grants").default(0),
  errors:        text("errors"),
  durationSec:   real("duration_sec"),
});

export type ScanLog = typeof scanLogs.$inferSelect;
