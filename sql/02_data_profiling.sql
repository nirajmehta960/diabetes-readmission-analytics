-- Data profiling queries for diabetic_data
-- Run against the raw table after load. Expect ~101,766 records, 50 columns.

-- Total record count
SELECT COUNT(*) AS total_records FROM diabetic_data;

-- Column null analysis (for key columns; '?' used for missing in raw CSV)
SELECT
  SUM(CASE WHEN race = '?' THEN 1 ELSE 0 END) AS race_missing,
  SUM(CASE WHEN weight = '?' THEN 1 ELSE 0 END) AS weight_missing,
  SUM(CASE WHEN payer_code = '?' THEN 1 ELSE 0 END) AS payer_missing,
  SUM(CASE WHEN medical_specialty = '?' THEN 1 ELSE 0 END) AS specialty_missing,
  COUNT(*) AS total
FROM diabetic_data;

-- Target variable distribution
SELECT readmitted, COUNT(*) AS cnt,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM diabetic_data
GROUP BY readmitted;

-- Duplicate patient check
SELECT COUNT(DISTINCT patient_nbr) AS unique_patients,
  COUNT(*) AS total_encounters
FROM diabetic_data;

-- Age distribution
SELECT age, COUNT(*) AS cnt
FROM diabetic_data
GROUP BY age ORDER BY age;

-- Readmission rate by age group
SELECT age,
  SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
  COUNT(*) AS total,
  ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
GROUP BY age ORDER BY age;

-- Medical specialty cardinality and missingness
SELECT COUNT(DISTINCT medical_specialty) AS unique_specialties,
  SUM(CASE WHEN medical_specialty = '?' THEN 1 ELSE 0 END) AS missing_count
FROM diabetic_data;

-- Top 10 medical specialties by volume
SELECT medical_specialty, COUNT(*) AS cnt
FROM diabetic_data
WHERE medical_specialty != '?'
GROUP BY medical_specialty
ORDER BY cnt DESC LIMIT 10;

-- Diagnosis code cardinality
SELECT COUNT(DISTINCT diag_1) AS diag1_unique,
  COUNT(DISTINCT diag_2) AS diag2_unique,
  COUNT(DISTINCT diag_3) AS diag3_unique
FROM diabetic_data;

-- Prior utilization summary
SELECT
  ROUND(AVG(number_inpatient), 2) AS avg_inpatient,
  MAX(number_inpatient) AS max_inpatient,
  ROUND(AVG(number_outpatient), 2) AS avg_outpatient,
  ROUND(AVG(number_emergency), 2) AS avg_emergency
FROM diabetic_data;
