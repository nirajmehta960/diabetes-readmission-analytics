-- ============================================================
-- SQL ETL PIPELINE (SQLite) — MARTS / ANALYTICS VIEWS
-- These are "consumption-ready" views for BI and analysis.
-- ============================================================

DROP VIEW IF EXISTS mart_readmission_kpis;
DROP VIEW IF EXISTS mart_readmission_by_age_diag;
DROP VIEW IF EXISTS mart_readmission_by_specialty;
DROP VIEW IF EXISTS mart_high_utilizers;

-- 1) Simple KPI view
CREATE VIEW mart_readmission_kpis AS
SELECT
  COUNT(*) AS total_encounters,
  SUM(readmit_30) AS readmit_30_count,
  ROUND(SUM(readmit_30) * 100.0 / COUNT(*), 2) AS readmit_30_rate_pct,
  ROUND(AVG(time_in_hospital), 2) AS avg_los_days,
  ROUND(AVG(num_medications), 2) AS avg_num_medications
FROM fct_encounters;

-- 2) Readmission by age and primary diagnosis category
CREATE VIEW mart_readmission_by_age_diag AS
SELECT
  age,
  diag_1_category,
  COUNT(*) AS total,
  SUM(readmit_30) AS readmit_30,
  ROUND(SUM(readmit_30) * 100.0 / COUNT(*), 2) AS readmit_rate_pct
FROM fct_encounters
GROUP BY age, diag_1_category
HAVING COUNT(*) >= 50
ORDER BY age, readmit_rate_pct DESC;

-- 3) Specialty slice
CREATE VIEW mart_readmission_by_specialty AS
SELECT
  medical_specialty,
  COUNT(*) AS total,
  SUM(readmit_30) AS readmit_30,
  ROUND(SUM(readmit_30) * 100.0 / COUNT(*), 2) AS readmit_rate_pct
FROM fct_encounters
GROUP BY medical_specialty
HAVING COUNT(*) >= 100
ORDER BY readmit_rate_pct DESC, total DESC;

-- 4) High utilizer report
CREATE VIEW mart_high_utilizers AS
SELECT
  utilization_tier,
  COUNT(*) AS total,
  SUM(readmit_30) AS readmit_30,
  ROUND(SUM(readmit_30) * 100.0 / COUNT(*), 2) AS readmit_rate_pct,
  ROUND(AVG(num_medications), 2) AS avg_num_meds,
  ROUND(AVG(time_in_hospital), 2) AS avg_los_days
FROM fct_encounters
GROUP BY utilization_tier
ORDER BY
  CASE utilization_tier
    WHEN 'High Utilization' THEN 1
    WHEN 'Medium Utilization' THEN 2
    WHEN 'Low Utilization' THEN 3
    WHEN 'No Prior Visits' THEN 4
    ELSE 5
  END;

