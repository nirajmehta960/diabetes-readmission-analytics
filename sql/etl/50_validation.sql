-- ============================================================
-- SQL ETL PIPELINE (SQLite) — VALIDATION / SMOKE TESTS
-- Lightweight checks to confirm key tables/views are populated.
-- These are safe to re-run after each ETL execution.
-- ============================================================

-- Row counts for core tables
SELECT 'stg_encounters' AS table_name, COUNT(*) AS row_count FROM stg_encounters
UNION ALL
SELECT 'fct_encounters' AS table_name, COUNT(*) AS row_count FROM fct_encounters
UNION ALL
SELECT 'fct_patient_latest' AS table_name, COUNT(*) AS row_count FROM fct_patient_latest;

-- Row counts for dimensions
SELECT 'dim_admission_type' AS table_name, COUNT(*) AS row_count FROM dim_admission_type
UNION ALL
SELECT 'dim_discharge_disposition' AS table_name, COUNT(*) AS row_count FROM dim_discharge_disposition
UNION ALL
SELECT 'dim_admission_source' AS table_name, COUNT(*) AS row_count FROM dim_admission_source
UNION ALL
SELECT 'dim_medical_specialty' AS table_name, COUNT(*) AS row_count FROM dim_medical_specialty;

-- Check primary mart KPIs roughly align with expectations
SELECT * FROM mart_readmission_kpis;

