-- Migracja 002: dodanie kolumny track do tabeli grants
-- Uruchom w Supabase: Dashboard → SQL Editor → wklej i kliknij RUN

-- Typ enum dla track
DO $$ BEGIN
  CREATE TYPE grant_track AS ENUM ('JST', 'R&D', 'EU_DIRECT');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Dodaj kolumnę track
ALTER TABLE grants
  ADD COLUMN IF NOT EXISTS track grant_track DEFAULT NULL;

-- Oznacz istniejące granty na podstawie source_name i programme
UPDATE grants SET track = 'R&D'
WHERE source_name ILIKE '%EIC%'
   OR source_name ILIKE '%NCBR%'
   OR source_name ILIKE '%Eurostars%'
   OR programme ILIKE '%Horizon%'
   OR programme ILIKE '%FENG%'
   OR programme ILIKE '%KPO%';

UPDATE grants SET track = 'JST'
WHERE source_name ILIKE '%EUI%'
   OR source_name ILIKE '%Urban Initiative%'
   OR source_name ILIKE '%Interreg%'
   OR programme ILIKE '%ERDF%'
   OR programme ILIKE '%Urban%';

UPDATE grants SET track = 'EU_DIRECT'
WHERE source_name ILIKE '%CEF%'
   OR source_name ILIKE '%LIFE%'
   OR source_name ILIKE '%EIT%'
   OR programme ILIKE '%CEF%'
   OR programme ILIKE '%LIFE%';

-- Podgląd wyników
SELECT track, count(*) FROM grants GROUP BY track;
