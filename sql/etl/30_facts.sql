-- ============================================================
-- SQL ETL PIPELINE (SQLite) — FACTS
-- Builds encounter and patient-level facts + derived groupings.
-- ============================================================

-- Helper: diagnosis category mapping (Strack-style groupings).
-- SQLite lacks TRY_CAST, so we guard numeric casts by pattern.
DROP VIEW IF EXISTS vw_encounters_enriched;

CREATE VIEW vw_encounters_enriched AS
SELECT
  e.*,

  -- Diagnosis group for diag_1 (primary)
  CASE
    WHEN e.diag_1 IS NULL THEN 'Unknown'
    WHEN e.diag_1 LIKE 'V%' OR e.diag_1 LIKE 'E%' THEN 'Other'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 390 AND 459 OR (CAST(e.diag_1 AS REAL) >= 785 AND CAST(e.diag_1 AS REAL) < 786)) THEN 'Circulatory'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 460 AND 519 OR (CAST(e.diag_1 AS REAL) >= 786 AND CAST(e.diag_1 AS REAL) < 787)) THEN 'Respiratory'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 520 AND 579 OR (CAST(e.diag_1 AS REAL) >= 787 AND CAST(e.diag_1 AS REAL) < 788)) THEN 'Digestive'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 250 AND 250.99) THEN 'Diabetes'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 800 AND 999) THEN 'Injury'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 710 AND 739) THEN 'Musculoskeletal'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 580 AND 629 OR (CAST(e.diag_1 AS REAL) >= 788 AND CAST(e.diag_1 AS REAL) < 789)) THEN 'Genitourinary'
    WHEN e.diag_1 GLOB '[0-9]*' AND (CAST(e.diag_1 AS REAL) BETWEEN 140 AND 239) THEN 'Neoplasms'
    ELSE 'Other'
  END AS diag_1_category,

  -- Discharge disposition grouping (high-level)
  CASE
    WHEN e.discharge_disposition_id IN (1, 6, 8) THEN 'Home'
    WHEN e.discharge_disposition_id IN (2, 3, 4, 5, 15, 22, 23, 24, 30) THEN 'Transfer/Facility'
    WHEN e.discharge_disposition_id IN (11, 13, 14, 19, 20, 21) THEN 'Expired/Hospice'
    WHEN e.discharge_disposition_id IN (9, 12) THEN 'Still Inpatient'
    ELSE 'Other/Unknown'
  END AS discharge_group,

  -- Admission type grouping
  CASE
    WHEN e.admission_type_id = 1 THEN 'Emergency'
    WHEN e.admission_type_id = 2 THEN 'Urgent'
    WHEN e.admission_type_id = 3 THEN 'Elective'
    WHEN e.admission_type_id = 4 THEN 'Newborn'
    WHEN e.admission_type_id = 7 THEN 'Trauma'
    ELSE 'Other/Unknown'
  END AS admission_type_group,

  -- Medication complexity proxy: count of selected meds that are not 'No'
  (
    CASE WHEN e.metformin IS NOT NULL AND e.metformin != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.repaglinide IS NOT NULL AND e.repaglinide != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.glimepiride IS NOT NULL AND e.glimepiride != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.glipizide IS NOT NULL AND e.glipizide != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.glyburide IS NOT NULL AND e.glyburide != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.pioglitazone IS NOT NULL AND e.pioglitazone != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.rosiglitazone IS NOT NULL AND e.rosiglitazone != 'No' THEN 1 ELSE 0 END +
    CASE WHEN e.insulin IS NOT NULL AND e.insulin != 'No' THEN 1 ELSE 0 END
  ) AS med_changes_selected
FROM stg_encounters e;

-- Encounter fact table
DROP TABLE IF EXISTS fct_encounters;

CREATE TABLE fct_encounters AS
SELECT
  encounter_id,
  patient_nbr,
  race,
  gender,
  age,
  admission_type_id,
  discharge_disposition_id,
  admission_source_id,
  medical_specialty,
  time_in_hospital,
  num_lab_procedures,
  num_procedures,
  num_medications,
  number_outpatient,
  number_emergency,
  number_inpatient,
  number_diagnoses,
  diag_1,
  diag_2,
  diag_3,
  diag_1_category,
  discharge_group,
  admission_type_group,
  a1c_result,
  a1c_tested,
  med_change_flag,
  diabetes_med,
  med_changes_selected,
  total_visits_prior,
  utilization_tier,
  readmitted,
  readmit_30
FROM vw_encounters_enriched;

CREATE INDEX IF NOT EXISTS idx_fct_encounters_patient ON fct_encounters(patient_nbr);
CREATE INDEX IF NOT EXISTS idx_fct_encounters_diagcat ON fct_encounters(diag_1_category);

-- Patient-level fact: latest encounter per patient (proxy for one-row-per-patient dataset)
DROP TABLE IF EXISTS fct_patient_latest;

CREATE TABLE fct_patient_latest AS
WITH ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY patient_nbr ORDER BY encounter_id DESC) AS rn
  FROM fct_encounters
)
SELECT
  patient_nbr,
  encounter_id AS latest_encounter_id,
  race,
  gender,
  age,
  medical_specialty,
  diag_1_category,
  discharge_group,
  admission_type_group,
  time_in_hospital,
  num_medications,
  num_lab_procedures,
  number_diagnoses,
  total_visits_prior,
  utilization_tier,
  a1c_tested,
  med_changes_selected,
  readmit_30
FROM ranked
WHERE rn = 1;

CREATE INDEX IF NOT EXISTS idx_fct_patient_latest_readmit ON fct_patient_latest(readmit_30);

