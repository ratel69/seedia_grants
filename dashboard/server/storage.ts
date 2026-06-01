import { db } from "./db";
import { grants, grantFiches, scanLogs } from "@shared/schema";
import type { Grant, InsertGrant, GrantFiche, InsertFiche, ScanLog } from "@shared/schema";
import { eq, desc, gte, lte, and, or, like, sql } from "drizzle-orm";
import { randomUUID } from "crypto";

export interface IStorage {
  // Grants
  getGrants(filters?: {
    status?: string;
    recommendedAction?: string;
    search?: string;
    minScore?: number;
    track?: string;
  }): Grant[];
  getGrantById(id: string): Grant | undefined;
  getGrantByUrl(url: string): Grant | undefined;
  upsertGrant(grant: InsertGrant): Grant;
  updateGrantStatus(id: string, status: string, owner?: string): Grant | undefined;
  // Fiches
  getFicheByGrantId(grantId: string): GrantFiche | undefined;
  upsertFiche(fiche: InsertFiche): GrantFiche;
  // Stats
  getStats(): {
    total: number;
    apply: number;
    strongWatch: number;
    watch: number;
    rejected: number;
    avgScore: number;
    withDeadline30d: number;
  };
  // Scan logs
  getScanLogs(limit?: number): ScanLog[];
}

export const storage: IStorage = {
  getGrants(filters = {}) {
    let query = db.select().from(grants);
    const conditions = [];

    if (filters.status) {
      conditions.push(eq(grants.status, filters.status));
    }
    if (filters.recommendedAction) {
      conditions.push(eq(grants.recommendedAction, filters.recommendedAction));
    }
    if (filters.minScore) {
      conditions.push(gte(grants.scoreTotal, filters.minScore));
    }
    if (filters.search) {
      const term = `%${filters.search}%`;
      conditions.push(
        or(
          like(grants.grantName, term),
          like(grants.sourceName, term),
          like(grants.programme, term)
        )
      );
    }
    if (filters.track) {
      conditions.push(eq((grants as any).track, filters.track));
    }

    if (conditions.length > 0) {
      return query.where(and(...conditions)).orderBy(desc(grants.scoreTotal)).all();
    }
    return query.orderBy(desc(grants.scoreTotal)).all();
  },

  getGrantById(id) {
    return db.select().from(grants).where(eq(grants.id, id)).get();
  },

  getGrantByUrl(url) {
    return db.select().from(grants).where(eq(grants.url, url)).get();
  },

  upsertGrant(grant) {
    const existing = grant.url ? db.select().from(grants).where(eq(grants.url, grant.url)).get() : undefined;
    const now = new Date().toISOString();

    if (existing) {
      return db.update(grants)
        .set({ ...grant, updatedAt: now })
        .where(eq(grants.id, existing.id))
        .returning()
        .get();
    }
    return db.insert(grants)
      .values({ ...grant, id: randomUUID(), createdAt: now, updatedAt: now })
      .returning()
      .get();
  },

  updateGrantStatus(id, status, owner) {
    const updates: Partial<Grant> = { status, updatedAt: new Date().toISOString() };
    if (owner) updates.owner = owner;
    return db.update(grants).set(updates).where(eq(grants.id, id)).returning().get();
  },

  getFicheByGrantId(grantId) {
    return db.select().from(grantFiches).where(eq(grantFiches.grantId, grantId)).get();
  },

  upsertFiche(fiche) {
    const existing = db.select().from(grantFiches).where(eq(grantFiches.grantId, fiche.grantId)).get();
    if (existing) {
      return db.update(grantFiches).set(fiche).where(eq(grantFiches.id, existing.id)).returning().get();
    }
    return db.insert(grantFiches).values({ ...fiche, id: randomUUID() }).returning().get();
  },

  getStats() {
    const all = db.select().from(grants).all();
    const today = new Date();
    const in30d = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
    const todayStr = today.toISOString().split("T")[0];

    return {
      total: all.length,
      apply: all.filter(g => g.recommendedAction === "apply").length,
      strongWatch: all.filter(g => g.recommendedAction === "strong watch").length,
      watch: all.filter(g => g.recommendedAction === "watch").length,
      rejected: all.filter(g => g.recommendedAction === "reject").length,
      avgScore: all.length > 0
        ? Math.round(all.reduce((s, g) => s + (g.scoreTotal || 0), 0) / all.length)
        : 0,
      withDeadline30d: all.filter(g =>
        g.deadline && g.deadline >= todayStr && g.deadline <= in30d
      ).length,
    };
  },

  getScanLogs(limit = 20) {
    return db.select().from(scanLogs).orderBy(desc(scanLogs.scannedAt)).limit(limit).all();
  },
};
