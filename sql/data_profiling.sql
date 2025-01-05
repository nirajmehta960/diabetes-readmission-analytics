-- ============================================================
-- DATA PROFILING QUERIES
-- Healthcare Analytics: Diabetes 130-US Hospitals (1999-2008)
-- Run against SQLite database loaded from diabetic_data.csv
-- ============================================================

-- 1. Dataset Overview: row count
SELECT COUNT(*) AS total_encounters FROM diabetes_data;

-- 2. Column-level null/missing analysis
-- Note: '?' values are loaded as NULL via pandas na_values='?'
SELECT
    SUM(CASE WHEN race IS NULL THEN 1 ELSE 0 END) AS missing_race,
    SUM(CASE WHEN weight IS NULL THEN 1 ELSE 0 END) AS missing_weight,
    SUM(CASE WHEN payer_code IS NULL THEN 1 ELSE 0 END) AS missing_payer,
    SUM(CASE WHEN medical_specialty IS NULL THEN 1 ELSE 0 END) AS missing_specialty,
    SUM(CASE WHEN max_glu_serum IS NULL THEN 1 ELSE 0 END) AS missing_glu_serum,
    SUM(CASE WHEN A1Cresult IS NULL THEN 1 ELSE 0 END) AS missing_a1c,
    SUM(CASE WHEN diag_1 IS NULL THEN 1 ELSE 0 END) AS missing_diag1,
    SUM(CASE WHEN diag_2 IS NULL THEN 1 ELSE 0 END) AS missing_diag2,
    SUM(CASE WHEN diag_3 IS NULL THEN 1 ELSE 0 END) AS missing_diag3,
    COUNT(*) AS total_rows
FROM diabetes_data;

-- 3. Target variable distribution (readmission status)
SELECT
    readmitted,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM diabetes_data
GROUP BY readmitted
ORDER BY count DESC;

-- 4. Unique patients vs. total encounters (duplicate detection)
SELECT
    COUNT(*) AS total_encounters,
    COUNT(DISTINCT patient_nbr) AS unique_patients,
    COUNT(*) - COUNT(DISTINCT patient_nbr) AS duplicate_encounters
FROM diabetes_data;

-- 5. Age distribution by readmission status
SELECT
    age,
    readmitted,
    COUNT(*) AS patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY age), 2) AS pct_within_age
FROM diabetes_data
GROUP BY age, readmitted
ORDER BY age, readmitted;

-- 6. Race distribution by readmission status
SELECT
    COALESCE(race, 'Unknown') AS race,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_30_rate
FROM diabetes_data
GROUP BY race
ORDER BY total DESC;

-- 7. Gender distribution
SELECT
    gender,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_30_rate
FROM diabetes_data
GROUP BY gender
ORDER BY total DESC;

-- 8. Top 15 medical specialties by readmission rate (min 100 encounters)
SELECT
    medical_specialty,
    COUNT(*) AS total_encounters,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetes_data
WHERE medical_specialty IS NOT NULL
GROUP BY medical_specialty
HAVING COUNT(*) > 100
ORDER BY readmit_rate DESC
LIMIT 15;

-- 9. Impact of HbA1c testing on readmission
SELECT
    CASE WHEN A1Cresult IS NULL THEN 'Not Tested' ELSE 'Tested' END AS hba1c_status,
    readmitted,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY
        CASE WHEN A1Cresult IS NULL THEN 'Not Tested' ELSE 'Tested' END), 2) AS pct
FROM diabetes_data
GROUP BY hba1c_status, readmitted
ORDER BY hba1c_status, readmitted;

-- 10. Prior inpatient visits vs. readmission
SELECT
    CASE
        WHEN number_inpatient = 0 THEN '0'
        WHEN number_inpatient = 1 THEN '1'
        WHEN number_inpatient BETWEEN 2 AND 3 THEN '2-3'
        ELSE '4+'
    END AS prior_inpatient_group,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetes_data
GROUP BY prior_inpatient_group
ORDER BY readmit_rate;

-- 11. Time in hospital statistics by readmission status
SELECT
    readmitted,
    ROUND(AVG(time_in_hospital), 2) AS avg_days,
    MIN(time_in_hospital) AS min_days,
    MAX(time_in_hospital) AS max_days,
    COUNT(*) AS count
FROM diabetes_data
GROUP BY readmitted
ORDER BY readmitted;

-- 12. Number of medications statistics by readmission status
SELECT
    readmitted,
    ROUND(AVG(num_medications), 2) AS avg_meds,
    MIN(num_medications) AS min_meds,
    MAX(num_medications) AS max_meds
FROM diabetes_data
GROUP BY readmitted
ORDER BY readmitted;

-- 13. Discharge disposition analysis
SELECT
    discharge_disposition_id,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetes_data
GROUP BY discharge_disposition_id
HAVING COUNT(*) > 50
ORDER BY readmit_rate DESC;

-- 14. Insulin usage and readmission
SELECT
    insulin,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetes_data
GROUP BY insulin
ORDER BY readmit_rate DESC;

-- 15. Diabetes medication change and readmission
SELECT
    change,
    diabetesMed,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetes_data
GROUP BY change, diabetesMed
ORDER BY readmit_rate DESC;
