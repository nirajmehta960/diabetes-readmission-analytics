# Data Dictionary — Diabetes 130-US Hospitals Dataset

## Raw data columns (50 columns)

### Identifiers (2)
| Column | Type | Description |
|--------|------|-------------|
| encounter_id | Integer | Unique ID for each hospital encounter |
| patient_nbr | Integer | Unique ID for each patient (one patient can have multiple encounters) |

### Demographics (3)
| Column | Type | Description |
|--------|------|-------------|
| race | Categorical | Patient's race: Caucasian, African American, Hispanic, Asian, Other, ? (~2% missing) |
| gender | Categorical | Male, Female, Unknown/Invalid (3 records) |
| age | Categorical | Age bracket in 10-year bins: [0-10), [10-20), ..., [90-100) |

### Encounter / Admission details (8)
| Column | Type | Description |
|--------|------|-------------|
| weight | Categorical | Weight range in pounds; ~97% missing as '?' |
| admission_type_id | Integer | How patient was admitted (maps via IDs_mapping.csv) |
| discharge_disposition_id | Integer | Where patient went after discharge (maps via IDs_mapping.csv) |
| admission_source_id | Integer | Where patient came from (maps via IDs_mapping.csv) |
| time_in_hospital | Integer | Length of stay in days (1–14) |
| payer_code | Categorical | Payment source; ~40% missing as '?' |
| medical_specialty | Categorical | Admitting physician's specialty (73 unique values); ~49% missing as '?' |
| num_lab_procedures | Integer | Number of lab tests performed during encounter (1–132) |

### Clinical utilization (4)
| Column | Type | Description |
|--------|------|-------------|
| num_procedures | Integer | Number of non-lab procedures during encounter (0–6) |
| num_medications | Integer | Number of distinct medications during encounter (1–81) |
| number_outpatient | Integer | Outpatient visits in the year before this hospitalization (0–42) |
| number_emergency | Integer | Emergency visits in the year before this hospitalization (0–76) |

### Prior visits and diagnoses (4)
| Column | Type | Description |
|--------|------|-------------|
| number_inpatient | Integer | Inpatient visits in the year before this hospitalization (0–21) — strongest readmission predictor |
| diag_1 | Categorical | Primary diagnosis ICD-9 code (~700 unique values) |
| diag_2 | Categorical | Secondary diagnosis ICD-9 code (~700 unique values) |
| diag_3 | Categorical | Tertiary diagnosis ICD-9 code (~700 unique values) |

### Diagnosis count (1)
| Column | Type | Description |
|--------|------|-------------|
| number_diagnoses | Integer | Total number of diagnoses entered for this encounter (1–16) |

### Lab results (2)
| Column | Type | Description |
|--------|------|-------------|
| max_glu_serum | Categorical | Glucose serum test result: >200, >300, normal, none |
| A1Cresult | Categorical | HbA1c test result: >7, >8, normal, none |

### Medication features (23)
Metformin, repaglinide, nateglinide, chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide, pioglitazone, rosiglitazone, acarbose, miglitol, troglitazone, tolazamide, examide, citoglipton, insulin, glyburide-metformin, glipizide-metformin, glimepiride-pioglitazone, metformin-rosiglitazone, metformin-pioglitazone. Each: No, Steady, Up, Down. (examide, citoglipton are near-zero variance.)

### Treatment summary (2)
| Column | Type | Description |
|--------|------|-------------|
| change | Binary | Whether any diabetic medication was changed: Ch (yes), No |
| diabetesMed | Binary | Whether any diabetes medication was prescribed: Yes, No |

### Target variable (1)
| Column | Type | Description |
|--------|------|-------------|
| readmitted | Categorical | "<30" (within 30 days), ">30" (after 30 days), "NO" (not readmitted) |

---

## Columns removed in preprocessing (Phase 2)

| Column dropped | Reason |
|----------------|--------|
| encounter_id | Identifier only |
| patient_nbr | Used for deduplication, then dropped |
| weight | ~97% missing |
| payer_code | ~40% missing; not a clinical feature |
| citoglipton | Near-zero variance |
| examide | Near-zero variance |

## Columns renamed in preprocessing

| Original | Renamed to | Transformation |
|----------|------------|----------------|
| diag_1 | diag_1_cat | ICD-9 codes to 9 clinical categories |
| diag_2 | diag_2_cat | ICD-9 codes to 9 clinical categories |
| diag_3 | diag_3_cat | ICD-9 codes to 9 clinical categories |
| readmitted | readmit_30 | 3-class to binary (0/1) target |

## Columns added in feature engineering (Phase 3)

| New column | Derived from | Purpose |
|------------|--------------|---------|
| total_visits_prior | number_outpatient + number_inpatient + number_emergency | Aggregate healthcare utilization |
| med_change_count | Count across 21 medication columns where value != "No" | Treatment complexity proxy |

## Pipeline summary

- **RAW (50 columns)** -> Phase 2 preprocessing -> **PREPROCESSED (44 columns)** -> diabetic_preprocessed.csv  
- Phase 3 feature engineering -> **FEATURED (46 columns)** -> diabetic_featured.csv  
- Phase 3 encoding -> **MODEL-READY (~100+ columns)** -> model_ready.csv
