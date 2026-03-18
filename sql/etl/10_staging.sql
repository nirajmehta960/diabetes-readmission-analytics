-- ============================================================
-- SQL ETL PIPELINE (SQLite) — STAGING
-- - Standardizes missing values ('?'=>NULL)
-- - Derives core labels/features used downstream
-- - Keeps encounter grain (one row per encounter_id)
-- ============================================================

DROP TABLE IF EXISTS stg_encounters;

CREATE TABLE stg_encounters AS
WITH base AS (
  SELECT
    CAST(encounter_id AS INTEGER) AS encounter_id,
    CAST(patient_nbr AS INTEGER) AS patient_nbr,

    NULLIF(race, '?') AS race,
    NULLIF(gender, '?') AS gender,
    NULLIF(age, '?') AS age,

    CAST(admission_type_id AS INTEGER) AS admission_type_id,
    CAST(discharge_disposition_id AS INTEGER) AS discharge_disposition_id,
    CAST(admission_source_id AS INTEGER) AS admission_source_id,

    CAST(time_in_hospital AS INTEGER) AS time_in_hospital,
    CAST(num_lab_procedures AS INTEGER) AS num_lab_procedures,
    CAST(num_procedures AS INTEGER) AS num_procedures,
    CAST(num_medications AS INTEGER) AS num_medications,
    CAST(number_outpatient AS INTEGER) AS number_outpatient,
    CAST(number_emergency AS INTEGER) AS number_emergency,
    CAST(number_inpatient AS INTEGER) AS number_inpatient,
    CAST(number_diagnoses AS INTEGER) AS number_diagnoses,

    NULLIF(medical_specialty, '?') AS medical_specialty,
    NULLIF(diag_1, '?') AS diag_1,
    NULLIF(diag_2, '?') AS diag_2,
    NULLIF(diag_3, '?') AS diag_3,

    NULLIF(max_glu_serum, '?') AS max_glu_serum,
    NULLIF(A1Cresult, '?') AS a1c_result,

    -- Med fields (kept as-is for med-change features; '?' rarely appears but normalize anyway)
    NULLIF(metformin, '?') AS metformin,
    NULLIF(repaglinide, '?') AS repaglinide,
    NULLIF(glimepiride, '?') AS glimepiride,
    NULLIF(glipizide, '?') AS glipizide,
    NULLIF(glyburide, '?') AS glyburide,
    NULLIF(pioglitazone, '?') AS pioglitazone,
    NULLIF(rosiglitazone, '?') AS rosiglitazone,
    NULLIF(insulin, '?') AS insulin,

    NULLIF(change, '?') AS med_change_flag,
    NULLIF(diabetesMed, '?') AS diabetes_med,

    readmitted
  FROM diabetic_data
)
SELECT
  encounter_id,
  patient_nbr,
  COALESCE(race, 'Unknown') AS race,
  COALESCE(gender, 'Unknown') AS gender,
  COALESCE(age, 'Unknown') AS age,
  admission_type_id,
  discharge_disposition_id,
  admission_source_id,
  time_in_hospital,
  num_lab_procedures,
  num_procedures,
  num_medications,
  number_outpatient,
  number_emergency,
  number_inpatient,
  number_diagnoses,
  COALESCE(medical_specialty, 'Unknown') AS medical_specialty,
  diag_1,
  diag_2,
  diag_3,
  max_glu_serum,
  a1c_result,

  repaglinide,
  metformin,
  glimepiride,
  glipizide,
  glyburide,
  pioglitazone,
  rosiglitazone,
  insulin,

  med_change_flag,
  diabetes_med,
  readmitted,
  CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END AS readmit_30,

  (number_outpatient + number_emergency + number_inpatient) AS total_visits_prior,
  CASE
    WHEN (number_outpatient + number_emergency + number_inpatient) = 0 THEN 'No Prior Visits'
    WHEN (number_outpatient + number_emergency + number_inpatient) BETWEEN 1 AND 3 THEN 'Low Utilization'
    WHEN (number_outpatient + number_emergency + number_inpatient) BETWEEN 4 AND 7 THEN 'Medium Utilization'
    ELSE 'High Utilization'
  END AS utilization_tier,

  CASE WHEN a1c_result IS NULL OR a1c_result = 'None' THEN 0 ELSE 1 END AS a1c_tested
FROM base;

CREATE INDEX IF NOT EXISTS idx_stg_encounters_patient ON stg_encounters(patient_nbr);
CREATE INDEX IF NOT EXISTS idx_stg_encounters_readmit30 ON stg_encounters(readmit_30);

