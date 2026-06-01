import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "@shared/schema";
import path from "path";

const DB_PATH = process.env.DB_PATH || path.join(process.cwd(), "data.db");
const sqlite = new Database(DB_PATH);
sqlite.pragma("journal_mode = WAL");

export const db = drizzle(sqlite, { schema });

// Initialize tables
sqlite.exec(`
  CREATE TABLE IF NOT EXISTS grants (
    id TEXT PRIMARY KEY,
    grant_name TEXT NOT NULL,
    source_name TEXT,
    programme TEXT,
    url TEXT UNIQUE,
    opening_date TEXT,
    deadline TEXT,
    funding_amount_min INTEGER,
    funding_amount_max INTEGER,
    funding_rate INTEGER,
    own_contribution_required INTEGER,
    own_contribution_pct INTEGER,
    eligible_applicants TEXT,
    eligible_countries TEXT,
    project_type TEXT,
    seedia_products_fit TEXT,
    fit_smart_city INTEGER,
    fit_micromobility INTEGER,
    fit_renewable_energy INTEGER,
    fit_data_ai INTEGER,
    fit_urban_infrastructure INTEGER,
    fit_resilience INTEGER,
    score_total INTEGER,
    score_reasoning TEXT,
    risk_level TEXT,
    key_risks TEXT,
    recommended_action TEXT,
    suggested_concept TEXT,
    next_action TEXT,
    status TEXT DEFAULT 'new',
    owner TEXT,
    ai_extracted INTEGER DEFAULT 0,
    ai_extracted_at TEXT,
    alert_sent INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
  );

  CREATE TABLE IF NOT EXISTS grant_fiches (
    id TEXT PRIMARY KEY,
    grant_id TEXT NOT NULL,
    content_md TEXT NOT NULL,
    generated_at TEXT
  );

  CREATE TABLE IF NOT EXISTS scan_logs (
    id TEXT PRIMARY KEY,
    source_name TEXT,
    scanned_at TEXT,
    new_grants INTEGER DEFAULT 0,
    updated_grants INTEGER DEFAULT 0,
    errors TEXT,
    duration_sec REAL
  );

  CREATE INDEX IF NOT EXISTS idx_grants_score ON grants(score_total DESC);
  CREATE INDEX IF NOT EXISTS idx_grants_deadline ON grants(deadline ASC);
  CREATE INDEX IF NOT EXISTS idx_grants_action ON grants(recommended_action);
  CREATE INDEX IF NOT EXISTS idx_grants_status ON grants(status);
`);
