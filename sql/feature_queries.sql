-- ============================================================
-- FEATURE ENGINEERING QUERIES
-- Healthcare Analytics: Diabetes 130-US Hospitals (1999-2008)
-- SQL-based feature analysis and engineering
-- ============================================================

-- 1. Create aggregate prior utilization metric
SELECT
    patient_nbr,
    (number_outpatient + number_inpatient + number_emergency) AS total_visits_prior,
    readmitted
FROM diabetic_data
ORDER BY total_visits_prior DESC
LIMIT 20;

-- 2. Risk stratification by combined prior utilization
SELECT
    CASE
        WHEN (number_outpatient + number_inpatient + number_emergency) = 0 THEN 'No Prior Visits'
        WHEN (number_outpatient + number_inpatient + number_emergency) BETWEEN 1 AND 3 THEN 'Low Utilization'
        WHEN (number_outpatient + number_inpatient + number_emergency) BETWEEN 4 AND 7 THEN 'Medium Utilization'
        ELSE 'High Utilization'
    END AS utilization_tier,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate_30
FROM diabetic_data
GROUP BY utilization_tier
ORDER BY readmit_rate_30 DESC;

-- 3. ICD-9 diagnosis grouping for primary diagnosis (diag_1)
-- Maps codes to broad clinical categories per Strack et al. paper
SELECT
    CASE
        WHEN diag_1 LIKE 'V%' OR diag_1 LIKE 'E%' THEN 'Other'
        WHEN CAST(diag_1 AS REAL) BETWEEN 390 AND 459 OR CAST(diag_1 AS REAL) = 785 THEN 'Circulatory'
        WHEN CAST(diag_1 AS REAL) BETWEEN 460 AND 519 OR CAST(diag_1 AS REAL) = 786 THEN 'Respiratory'
        WHEN CAST(diag_1 AS REAL) BETWEEN 520 AND 579 OR CAST(diag_1 AS REAL) = 787 THEN 'Digestive'
        WHEN CAST(diag_1 AS REAL) BETWEEN 250 AND 250.99 THEN 'Diabetes'
        WHEN CAST(diag_1 AS REAL) BETWEEN 800 AND 999 THEN 'Injury'
        WHEN CAST(diag_1 AS REAL) BETWEEN 710 AND 739 THEN 'Musculoskeletal'
        WHEN CAST(diag_1 AS REAL) BETWEEN 580 AND 629 OR CAST(diag_1 AS REAL) = 788 THEN 'Genitourinary'
        WHEN CAST(diag_1 AS REAL) BETWEEN 140 AND 239 THEN 'Neoplasms'
        ELSE 'Other'
    END AS diagnosis_category,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
WHERE diag_1 IS NOT NULL
GROUP BY diagnosis_category
ORDER BY readmit_rate DESC;

-- 4. Medication change analysis — count how many meds changed per patient
SELECT
    med_changes,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM (
    SELECT
        readmitted,
        (CASE WHEN metformin != 'No' THEN 1 ELSE 0 END +
         CASE WHEN repaglinide != 'No' THEN 1 ELSE 0 END +
         CASE WHEN glimepiride != 'No' THEN 1 ELSE 0 END +
         CASE WHEN glipizide != 'No' THEN 1 ELSE 0 END +
         CASE WHEN glyburide != 'No' THEN 1 ELSE 0 END +
         CASE WHEN pioglitazone != 'No' THEN 1 ELSE 0 END +
         CASE WHEN rosiglitazone != 'No' THEN 1 ELSE 0 END +
         CASE WHEN insulin != 'No' THEN 1 ELSE 0 END) AS med_changes
    FROM diabetic_data
) sub
GROUP BY med_changes
ORDER BY med_changes;

-- 5. Discharge disposition grouping
-- Groups the 30 disposition IDs into clinically meaningful categories
SELECT
    CASE
        WHEN discharge_disposition_id IN (1, 6, 8) THEN 'Home'
        WHEN discharge_disposition_id IN (2, 3, 4, 5, 15, 22, 23, 24, 30) THEN 'Transfer/Facility'
        WHEN discharge_disposition_id IN (11, 13, 14, 19, 20, 21) THEN 'Expired/Hospice'
        WHEN discharge_disposition_id IN (9, 12) THEN 'Still Inpatient'
        ELSE 'Other/Unknown'
    END AS discharge_group,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
GROUP BY discharge_group
ORDER BY readmit_rate DESC;

-- 6. Admission type grouping
SELECT
    CASE
        WHEN admission_type_id = 1 THEN 'Emergency'
        WHEN admission_type_id = 2 THEN 'Urgent'
        WHEN admission_type_id = 3 THEN 'Elective'
        WHEN admission_type_id = 4 THEN 'Newborn'
        WHEN admission_type_id = 7 THEN 'Trauma'
        ELSE 'Other/Unknown'
    END AS admission_type,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
GROUP BY admission_type
ORDER BY readmit_rate DESC;

-- 7. Interaction: age group × primary diagnosis category → readmission rate
SELECT
    age,
    CASE
        WHEN CAST(diag_1 AS REAL) BETWEEN 390 AND 459 OR CAST(diag_1 AS REAL) = 785 THEN 'Circulatory'
        WHEN CAST(diag_1 AS REAL) BETWEEN 460 AND 519 OR CAST(diag_1 AS REAL) = 786 THEN 'Respiratory'
        WHEN CAST(diag_1 AS REAL) BETWEEN 250 AND 250.99 THEN 'Diabetes'
        ELSE 'Other'
    END AS diag_group,
    COUNT(*) AS total,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
WHERE diag_1 IS NOT NULL
GROUP BY age, diag_group
HAVING COUNT(*) > 50
ORDER BY age, diag_group;

-- 8. Number of diagnoses vs. readmission (complexity indicator)
SELECT
    CASE
        WHEN number_diagnoses BETWEEN 1 AND 3 THEN '1-3'
        WHEN number_diagnoses BETWEEN 4 AND 6 THEN '4-6'
        WHEN number_diagnoses BETWEEN 7 AND 9 THEN '7-9'
        ELSE '9+'
    END AS diagnosis_count_group,
    COUNT(*) AS total,
    SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmit_30,
    ROUND(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS readmit_rate
FROM diabetic_data
GROUP BY diagnosis_count_group
ORDER BY diagnosis_count_group;
