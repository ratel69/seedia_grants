-- ============================================================
-- SEEDiA Grant Intelligence System — Initial Schema
-- ============================================================

-- SOURCES — lista monitorowanych źródeł
CREATE TABLE IF NOT EXISTS sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    url             TEXT NOT NULL UNIQUE,
    programme       TEXT,                  -- Horizon / EIT / PARP / NCBR / LIFE / Interreg
    priority        INTEGER DEFAULT 2,     -- 1=wysoki, 2=średni, 3=niski
    active          BOOLEAN DEFAULT TRUE,
    last_checked_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- GRANTS — główna tabela naborów
CREATE TABLE IF NOT EXISTS grants (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id                   UUID REFERENCES sources(id) ON DELETE SET NULL,

    -- Identyfikacja
    grant_name                  TEXT NOT NULL,
    source_name                 TEXT,
    programme                   TEXT,
    url                         TEXT UNIQUE,
    raw_content                 TEXT,          -- surowy tekst ze strony/PDF

    -- Daty
    opening_date                DATE,
    deadline                    DATE,
    decision_date               DATE,

    -- Finansowanie
    funding_amount_min          BIGINT,        -- EUR
    funding_amount_max          BIGINT,        -- EUR
    funding_rate                INTEGER,       -- % dofinansowania np. 70
    own_contribution_required   BOOLEAN,
    own_contribution_pct        INTEGER,       -- % wkładu własnego

    -- Kwalifikowalność
    eligible_applicants         TEXT[],        -- ['MŚP', 'konsorcjum', 'miasto']
    eligible_countries          TEXT[],        -- ['PL', 'UE', 'associated countries']
    project_type                TEXT,          -- pilotaż / B+R / demonstrator / scale-up

    -- Dopasowanie SEEDiA
    seedia_products_fit         TEXT[],        -- ['jCharge', 'solar shelter', ...]
    fit_smart_city              INTEGER CHECK (fit_smart_city BETWEEN 0 AND 5),
    fit_micromobility           INTEGER CHECK (fit_micromobility BETWEEN 0 AND 5),
    fit_renewable_energy        INTEGER CHECK (fit_renewable_energy BETWEEN 0 AND 5),
    fit_data_ai                 INTEGER CHECK (fit_data_ai BETWEEN 0 AND 5),
    fit_urban_infrastructure    INTEGER CHECK (fit_urban_infrastructure BETWEEN 0 AND 5),
    fit_resilience              INTEGER CHECK (fit_resilience BETWEEN 0 AND 5),

    -- Scoring
    score_total                 INTEGER CHECK (score_total BETWEEN 0 AND 100),
    score_reasoning             TEXT,
    risk_level                  TEXT CHECK (risk_level IN ('niski', 'średni', 'wysoki')),
    key_risks                   TEXT,

    -- Rekomendacja
    recommended_action          TEXT CHECK (recommended_action IN ('apply', 'strong watch', 'watch', 'reject')),
    suggested_concept           TEXT,          -- 5-zdaniowa koncepcja projektu
    next_action                 TEXT,

    -- Status procesowania
    status                      TEXT DEFAULT 'new' CHECK (status IN (
                                    'new', 'reviewed', 'in preparation',
                                    'submitted', 'won', 'rejected', 'archived'
                                )),
    owner                       TEXT,          -- osoba odpowiedzialna

    -- Integracje (faza 2)
    calendar_event_id           TEXT,
    crm_deal_id                 TEXT,
    asana_task_id               TEXT,

    -- Meta
    ai_extracted                BOOLEAN DEFAULT FALSE,
    ai_extracted_at             TIMESTAMPTZ,
    alert_sent                  BOOLEAN DEFAULT FALSE,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- GRANT_FICHES — fiszki (1-stronicowe streszczenia)
CREATE TABLE IF NOT EXISTS grant_fiches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id        UUID REFERENCES grants(id) ON DELETE CASCADE,
    content_md      TEXT NOT NULL,     -- treść fiszki w Markdown
    content_pdf_url TEXT,              -- link do PDF jeśli wygenerowany
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- SCAN_LOGS — logi codziennych skanów
CREATE TABLE IF NOT EXISTS scan_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID REFERENCES sources(id) ON DELETE SET NULL,
    source_name     TEXT,
    scanned_at      TIMESTAMPTZ DEFAULT NOW(),
    new_grants      INTEGER DEFAULT 0,
    updated_grants  INTEGER DEFAULT 0,
    errors          TEXT,
    duration_sec    FLOAT
);

-- ALERTS — historia wysłanych alertów
CREATE TABLE IF NOT EXISTS alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id        UUID REFERENCES grants(id) ON DELETE CASCADE,
    alert_type      TEXT,              -- 'new_high_score' / 'deadline_30d' / 'deadline_14d' / 'deadline_7d' / 'deadline_2d'
    channel         TEXT,              -- 'slack' / 'email'
    sent_at         TIMESTAMPTZ DEFAULT NOW(),
    message         TEXT
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_grants_score      ON grants(score_total DESC);
CREATE INDEX IF NOT EXISTS idx_grants_deadline   ON grants(deadline ASC);
CREATE INDEX IF NOT EXISTS idx_grants_status     ON grants(status);
CREATE INDEX IF NOT EXISTS idx_grants_action     ON grants(recommended_action);
CREATE INDEX IF NOT EXISTS idx_grants_created    ON grants(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_grants_source     ON grants(source_id);

-- ============================================================
-- TRIGGER: auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER grants_updated_at
    BEFORE UPDATE ON grants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- SEED: źródła MVP
-- ============================================================
INSERT INTO sources (name, url, programme, priority) VALUES
    ('EU Funding & Tenders Portal',     'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals', 'Horizon / EU',     1),
    ('Horizon Europe Cluster 5',        'https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe/cluster-5-climate-energy-and-mobility_en', 'Horizon Europe', 1),
    ('EIT Urban Mobility',              'https://www.eiturbanmobility.eu/join-us/call-for-proposals/', 'EIT',              1),
    ('PARP — harmonogram naborów',      'https://www.parp.gov.pl/harmonogram-naborow', 'PARP',             1),
    ('NCBR — harmonogram konkursów',    'https://www.gov.pl/web/ncbr/harmonogram-konkursow-2026', 'NCBR',             1),
    ('Portal Funduszy Europejskich',    'https://funduszeeuropejskie.gov.pl/nabory-wnioskow/', 'FE PL',            2),
    ('LIFE / CINEA',                    'https://cinea.ec.europa.eu/life-calls-proposals-2026_en', 'LIFE',             2),
    ('Interreg',                        'https://interreg.eu/calls-for-projects/', 'Interreg',         2)
ON CONFLICT (url) DO NOTHING;
