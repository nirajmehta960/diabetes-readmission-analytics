"""
Cleaning functions for Diabetes 130-US Hospitals dataset.
Phase 2: handle missing values, deduplicate, drop unusable columns, map diagnoses, binarize target.
"""

import os
import pandas as pd
import numpy as np

# Default paths (relative to project root). Resolved when run as script or via run_data_pipeline.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RAW_PATH = os.path.join(_PROJECT_ROOT, "data", "raw", "diabetic_data.csv")
DEFAULT_IDS_PATH = os.path.join(_PROJECT_ROOT, "data", "raw", "IDs_mapping.csv")
DEFAULT_PREPROCESSED_PATH = os.path.join(_PROJECT_ROOT, "data", "preprocessed", "diabetic_preprocessed.csv")


def map_icd9(code):
    """Map ICD-9 code to clinical category per Strack et al. methodology."""
    if code == "Unknown" or (isinstance(code, float) and np.isnan(code)):
        return "Unknown"
    try:
        num = float(code)
    except (ValueError, TypeError):
        return "Other"
    if 390 <= num <= 459 or num == 785:
        return "Circulatory"
    elif 460 <= num <= 519 or num == 786:
        return "Respiratory"
    elif 520 <= num <= 579 or num == 787:
        return "Digestive"
    elif 250 <= num < 251:
        return "Diabetes"
    elif 800 <= num <= 999:
        return "Injury"
    elif 710 <= num <= 739:
        return "Musculoskeletal"
    elif (580 <= num <= 629) or num == 788:
        return "Genitourinary"
    elif 140 <= num <= 239:
        return "Neoplasms"
    else:
        return "Other"


def load_raw(data_path: str, ids_path: str = None):
    """Load raw CSV and optional IDs mapping."""
    df = pd.read_csv(data_path)
    ids_mapping = pd.read_csv(ids_path) if ids_path else None
    return df, ids_mapping


def replace_missing(df: pd.DataFrame, placeholder: str = "?") -> pd.DataFrame:
    """Replace placeholder string with NaN."""
    return df.replace(placeholder, np.nan)


def drop_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """Drop encounter_id. Call after dedup for patient_nbr."""
    return df.drop(columns=["encounter_id"], errors="ignore")


def deduplicate_patients(df: pd.DataFrame, subset: str = "patient_nbr", keep: str = "first") -> pd.DataFrame:
    """Keep one encounter per patient (longest stay if sorted by time_in_hospital desc)."""
    df = df.sort_values("time_in_hospital", ascending=False)
    df = df.drop_duplicates(subset=subset, keep=keep)
    return df.drop(columns=[subset], errors="ignore")


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill or drop missing: gender invalid rows dropped; race, specialty, diag filled with Unknown."""
    df = df[df["gender"] != "Unknown/Invalid"].copy()
    df["race"] = df["race"].fillna("Unknown")
    df["medical_specialty"] = df["medical_specialty"].fillna("Unknown")
    for col in ["diag_1", "diag_2", "diag_3"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    return df


def reduce_medical_specialty_cardinality(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Keep top N specialties by count; rest become 'Other'."""
    top_specialties = df["medical_specialty"].value_counts().nlargest(top_n).index.tolist()
    df["medical_specialty"] = df["medical_specialty"].apply(
        lambda x: x if x in top_specialties else "Other"
    )
    return df


def map_diagnosis_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map diag_1, diag_2, diag_3 to categories and rename to diag_1_cat, diag_2_cat, diag_3_cat."""
    for col in ["diag_1", "diag_2", "diag_3"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: "Unknown" if pd.isna(x) else map_icd9(x))
    df = df.rename(columns={"diag_1": "diag_1_cat", "diag_2": "diag_2_cat", "diag_3": "diag_3_cat"})
    return df


def binarize_target(df: pd.DataFrame, source_col: str = "readmitted", target_col: str = "readmit_30") -> pd.DataFrame:
    """Create binary target: 1 if readmitted within 30 days, else 0."""
    df[target_col] = (df[source_col] == "<30").astype(int)
    return df.drop(columns=[source_col], errors="ignore")


def drop_unusable_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop weight, payer_code, citoglipton, examide."""
    drop_cols = ["weight", "payer_code", "citoglipton", "examide"]
    return df.drop(columns=[c for c in drop_cols if c in df.columns])


def run_cleaning_pipeline(
    data_path: str = None,
    ids_path: str = None,
    save_path: str = None,
) -> pd.DataFrame:
    """
    Run full Phase 2 cleaning pipeline.
    Uses default paths when arguments are None (data/raw/, data/preprocessed/).
    """
    data_path = data_path or DEFAULT_RAW_PATH
    ids_path = ids_path if ids_path is not None else DEFAULT_IDS_PATH
    save_path = save_path if save_path is not None else DEFAULT_PREPROCESSED_PATH

    df, _ = load_raw(data_path, ids_path)
    print(f"Started with: {len(df):,} rows")
    df = replace_missing(df)
    df = drop_identifiers(df)
    df = deduplicate_patients(df)
    print(f"After dedup: {len(df):,} rows")
    df = handle_missing_values(df)
    print(f"After removing invalid gender rows: {len(df):,} rows")
    df = reduce_medical_specialty_cardinality(df)
    df = map_diagnosis_columns(df)
    if "readmitted" in df.columns:
        df = binarize_target(df)
    df = drop_unusable_columns(df)
    print(f"Final preprocessed rows: {len(df):,}")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    return df


if __name__ == "__main__":
    # Run preprocessing only: saves to data/preprocessed/diabetic_preprocessed.csv
    run_cleaning_pipeline()
    print(f"Preprocessed data saved to {DEFAULT_PREPROCESSED_PATH}")
