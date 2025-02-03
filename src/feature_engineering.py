"""
Feature creation functions for Diabetes 130-US Hospitals dataset.
Phase 3: add total_visits_prior, med_change_count; encoding for model_ready output.
"""

import os
import pandas as pd
import numpy as np

# Default paths (relative to project root). Resolved when run as script or via run_data_pipeline.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PREPROCESSED_PATH = os.path.join(_PROJECT_ROOT, "data", "preprocessed", "diabetic_preprocessed.csv")
DEFAULT_FEATURED_PATH = os.path.join(_PROJECT_ROOT, "data", "featured", "diabetic_featured.csv")
DEFAULT_MODEL_READY_PATH = os.path.join(_PROJECT_ROOT, "data", "featured", "model_ready.csv")


MEDICATION_COLS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide",
    "tolbutamide", "pioglitazone", "rosiglitazone", "acarbose",
    "miglitol", "troglitazone", "tolazamide", "insulin",
    "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone",
    "metformin-pioglitazone",
]


def add_total_visits_prior(df: pd.DataFrame) -> pd.DataFrame:
    """Add total_visits_prior = number_outpatient + number_inpatient + number_emergency."""
    df["total_visits_prior"] = (
        df["number_outpatient"] + df["number_inpatient"] + df["number_emergency"]
    )
    return df


def add_med_change_count(df: pd.DataFrame, medication_cols: list = None) -> pd.DataFrame:
    """Add med_change_count = count of medication columns where value != 'No'."""
    cols = medication_cols or [c for c in MEDICATION_COLS if c in df.columns]
    df["med_change_count"] = df[cols].apply(
        lambda row: sum(1 for val in row if val != "No"), axis=1
    )
    return df


def encode_medication_ordinal(df: pd.DataFrame, medication_cols: list = None) -> pd.DataFrame:
    """Ordinal encode medication columns: No=0, Steady=1, Up=2, Down=3."""
    med_mapping = {"No": 0, "Steady": 1, "Up": 2, "Down": 3}
    cols = medication_cols or [c for c in MEDICATION_COLS if c in df.columns]
    for col in cols:
        df[col] = df[col].map(med_mapping).fillna(0).astype(int)
    return df


def encode_binary_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Encode change, diabetesMed, gender to 0/1."""
    if "change" in df.columns:
        df["change"] = (df["change"] == "Ch").astype(int)
    if "diabetesMed" in df.columns:
        df["diabetesMed"] = (df["diabetesMed"] == "Yes").astype(int)
    if "gender" in df.columns:
        df["gender"] = (df["gender"] == "Male").astype(int)
    return df


def one_hot_encode_categoricals(
    df: pd.DataFrame,
    categorical_cols: list = None,
    drop_first: bool = True,
) -> pd.DataFrame:
    """One-hot encode categorical columns. Converts ID columns to string first."""
    default_cats = [
        "race", "age", "admission_type_id", "discharge_disposition_id",
        "admission_source_id", "max_glu_serum", "A1Cresult",
        "medical_specialty", "diag_1_cat", "diag_2_cat", "diag_3_cat",
    ]
    cats = categorical_cols or [c for c in default_cats if c in df.columns]
    for col in ["admission_type_id", "discharge_disposition_id", "admission_source_id"]:
        if col in df.columns and col in cats:
            df[col] = df[col].astype(str)
    return pd.get_dummies(df, columns=cats, drop_first=drop_first)


def add_aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add aggregate and engineered features."""
    df = add_total_visits_prior(df)
    df = add_med_change_count(df)
    
    df["high_utilizer"] = (df["total_visits_prior"] >= 3).astype(int)
    df["discharged_home"] = (df["discharge_disposition_id"] == 1).astype(int)
    df["meds_per_day"] = df["num_medications"] / df["time_in_hospital"]
    df["a1c_tested"] = df["A1Cresult"].notnull().astype(int)
    df["any_diabetes_diag"] = df[["diag_1_cat", "diag_2_cat", "diag_3_cat"]].isin(["Diabetes"]).any(axis=1).astype(int)
    df["complexity_score"] = df["number_diagnoses"] * df["num_medications"]
    
    return df


def run_encoding_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Apply ordinal, binary, and one-hot encoding for model-ready dataset."""
    df = encode_medication_ordinal(df)
    df = encode_binary_categoricals(df)
    df = one_hot_encode_categoricals(df)
    return df


def run_feature_engineering_pipeline(
    input_path: str = None,
    featured_path: str = None,
    model_ready_path: str = None,
) -> tuple:
    """
    Run full Phase 3: load preprocessed data, add aggregate features, save featured;
    then encode and save model_ready. Uses default paths when arguments are None.
    Returns (df_featured, df_model_ready).
    """
    input_path = input_path or DEFAULT_PREPROCESSED_PATH
    featured_path = featured_path or DEFAULT_FEATURED_PATH
    model_ready_path = model_ready_path or DEFAULT_MODEL_READY_PATH

    df = pd.read_csv(input_path)
    df = add_aggregate_features(df)
    os.makedirs(os.path.dirname(featured_path), exist_ok=True)
    df.to_csv(featured_path, index=False)
    df_encoded = run_encoding_pipeline(df.copy())
    df_encoded.to_csv(model_ready_path, index=False)
    return df, df_encoded


if __name__ == "__main__":
    # Run feature engineering only: reads data/preprocessed, writes to data/featured/
    run_feature_engineering_pipeline()
    print(f"Featured data saved to {DEFAULT_FEATURED_PATH}")
    print(f"Model-ready data saved to {DEFAULT_MODEL_READY_PATH}")
