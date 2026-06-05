-- Migration 003: Add DUAL_USE to grant_track enum
-- Run in Supabase SQL Editor

-- Dodaj nową wartość do istniejącego enuma grant_track
ALTER TYPE grant_track ADD VALUE IF NOT EXISTS 'DUAL_USE';

-- Weryfikacja
SELECT unnest(enum_range(NULL::grant_track)) AS track_values;
