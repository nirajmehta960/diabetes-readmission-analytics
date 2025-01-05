-- Load CSV into SQL database
-- Run after creating a database (e.g. SQLite) and loading diabetic_data.csv and IDs_mapping.csv
-- Schema reflects the 50-column raw dataset from UCI Diabetes 130-US Hospitals.

-- Example for SQLite: create table from CSV import
-- .mode csv
-- .import data/raw/diabetic_data.csv diabetic_data
-- .import data/raw/IDs_mapping.csv IDs_mapping

-- For reference: expected columns in diabetic_data
-- encounter_id, patient_nbr, race, gender, age, weight, admission_type_id,
-- discharge_disposition_id, admission_source_id, time_in_hospital, payer_code,
-- medical_specialty, num_lab_procedures, num_procedures, num_medications,
-- number_outpatient, number_emergency, number_inpatient, diag_1, diag_2, diag_3,
-- number_diagnoses, max_glu_serum, A1Cresult, metformin, repaglinide, nateglinide,
-- chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide,
-- pioglitazone, rosiglitazone, acarbose, miglitol, troglitazone, tolazamide,
-- examide, citoglipton, insulin, glyburide-metformin, glipizide-metformin,
-- glimepiride-pioglitazone, metformin-rosiglitazone, metformin-pioglitazone,
-- change, diabetesMed, readmitted

-- IDs_mapping: admission_type_id, discharge_disposition_id, admission_source_id
-- with description columns for join/lookup.
