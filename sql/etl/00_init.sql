-- ============================================================
-- SQL ETL PIPELINE (SQLite) — INIT
-- Creates curated tables/views from the raw UCI diabetes dataset.
--
-- Assumptions (raw load step happens outside SQL in sqlite3 CLI):
-- - Table `diabetic_data` exists (imported from data/diabetic_data.csv)
-- - Table `IDs_mapping` exists (imported from data/IDS_mapping.csv)
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Keep raw tables as-is; this script only creates curated layers.

