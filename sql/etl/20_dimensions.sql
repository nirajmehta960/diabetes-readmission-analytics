-- ============================================================
-- SQL ETL PIPELINE (SQLite) — DIMENSIONS
-- Builds small lookup dimensions from IDs_mapping and staged data.
-- ============================================================

DROP TABLE IF EXISTS dim_admission_type;
DROP TABLE IF EXISTS dim_discharge_disposition;
DROP TABLE IF EXISTS dim_admission_source;
DROP TABLE IF EXISTS dim_medical_specialty;

-- IDs_mapping mapping is structured with 3 sections. 
-- Section 1 (admission_type_id) starts at row 1 without a header row.
-- Section 2 starts at row 10 with header 'discharge_disposition_id'.
-- Section 3 starts at row 42 with header 'admission_source_id'.

CREATE TABLE dim_admission_type AS
WITH mapping AS (
  SELECT
    rowid AS rid,
    TRIM(admission_type_id) AS key_raw,
    TRIM(description) AS desc_raw,
    CASE
      WHEN rowid = 1 THEN 1
      WHEN rowid = 10 THEN 2
      WHEN rowid = 42 THEN 3
      ELSE NULL
    END AS section_id
  FROM IDs_mapping
),
tagged AS (
  SELECT
    rid, key_raw, desc_raw,
    MAX(section_id) OVER (ORDER BY rid) AS section_num
  FROM mapping
)
SELECT DISTINCT
  CAST(key_raw AS INTEGER) AS admission_type_id,
  desc_raw AS admission_type_desc
FROM tagged
WHERE section_num = 1
  AND key_raw GLOB '[0-9]*'
  AND key_raw != ''
  AND desc_raw IS NOT NULL
  AND desc_raw != 'NULL';

CREATE TABLE dim_discharge_disposition AS
WITH mapping AS (
  SELECT
    rowid AS rid,
    TRIM(admission_type_id) AS key_raw,
    TRIM(description) AS desc_raw,
    CASE
      WHEN rowid = 1 THEN 1
      WHEN rowid = 10 THEN 2
      WHEN rowid = 42 THEN 3
      ELSE NULL
    END AS section_id
  FROM IDs_mapping
),
tagged AS (
  SELECT
    rid, key_raw, desc_raw,
    MAX(section_id) OVER (ORDER BY rid) AS section_num
  FROM mapping
)
SELECT DISTINCT
  CAST(key_raw AS INTEGER) AS discharge_disposition_id,
  desc_raw AS discharge_disposition_desc
FROM tagged
WHERE section_num = 2
  AND key_raw GLOB '[0-9]*'
  AND key_raw != ''
  AND desc_raw IS NOT NULL
  AND desc_raw != 'NULL';

CREATE TABLE dim_admission_source AS
WITH mapping AS (
  SELECT
    rowid AS rid,
    TRIM(admission_type_id) AS key_raw,
    TRIM(description) AS desc_raw,
    CASE
      WHEN rowid = 1 THEN 1
      WHEN rowid = 10 THEN 2
      WHEN rowid = 42 THEN 3
      ELSE NULL
    END AS section_id
  FROM IDs_mapping
),
tagged AS (
  SELECT
    rid, key_raw, desc_raw,
    MAX(section_id) OVER (ORDER BY rid) AS section_num
  FROM mapping
)
SELECT DISTINCT
  CAST(key_raw AS INTEGER) AS admission_source_id,
  desc_raw AS admission_source_desc
FROM tagged
WHERE section_num = 3
  AND key_raw GLOB '[0-9]*'
  AND key_raw != ''
  AND desc_raw IS NOT NULL
  AND desc_raw != 'NULL';

-- Specialty dim from observed values
CREATE TABLE dim_medical_specialty AS
SELECT
  medical_specialty,
  COUNT(*) AS encounter_count
FROM stg_encounters
GROUP BY medical_specialty;

CREATE INDEX IF NOT EXISTS idx_dim_specialty ON dim_medical_specialty(medical_specialty);
