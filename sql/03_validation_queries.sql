-- Post-cleaning validation checks
-- Run against the preprocessed/cleaned table to verify Phase 2 output.

-- 1. No '?' values should remain in the dataset
-- (Adjust table/column names if your cleaned table differs)
-- SELECT COUNT(*) AS question_marks_remaining
-- FROM diabetic_preprocessed
-- WHERE race = '?' OR weight = '?' OR payer_code = '?' OR medical_specialty = '?'
--    OR diag_1 = '?' OR diag_2 = '?' OR diag_3 = '?';
-- Expected: 0

-- 2. Row count sanity check (after dedup: one row per patient, fewer than raw)
-- SELECT COUNT(*) AS row_count FROM diabetic_preprocessed;

-- 3. Verify identifier columns are dropped
-- (Should fail with "column not found" if schema is correct: encounter_id, patient_nbr)
-- SELECT encounter_id, patient_nbr FROM diabetic_preprocessed LIMIT 1;

-- 4. Verify renamed columns exist: diag_1_cat, diag_2_cat, diag_3_cat, readmit_30
-- SELECT diag_1_cat, diag_2_cat, diag_3_cat, readmit_30 FROM diabetic_preprocessed LIMIT 1;

-- 5. Verify dropped columns are gone: weight, payer_code, citoglipton, examide
-- SELECT weight, payer_code, citoglipton, examide FROM diabetic_preprocessed LIMIT 1;

-- 6. Target distribution (readmit_30 binary: expect ~0.11 mean)
-- SELECT readmit_30, COUNT(*) AS cnt,
--   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
-- FROM diabetic_preprocessed
-- GROUP BY readmit_30;

-- 7. No nulls in critical columns
-- SELECT
--   SUM(CASE WHEN race IS NULL THEN 1 ELSE 0 END) AS race_nulls,
--   SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS gender_nulls,
--   SUM(CASE WHEN medical_specialty IS NULL THEN 1 ELSE 0 END) AS specialty_nulls,
--   SUM(CASE WHEN diag_1_cat IS NULL THEN 1 ELSE 0 END) AS diag1_nulls,
--   SUM(CASE WHEN readmit_30 IS NULL THEN 1 ELSE 0 END) AS target_nulls
-- FROM diabetic_preprocessed;
-- Expected: all 0
