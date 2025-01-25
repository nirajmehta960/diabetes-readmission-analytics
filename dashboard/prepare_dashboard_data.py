"""
Prepare aggregated dashboard data from preprocessed or featured dataset.
Run from project root: python dashboard/prepare_dashboard_data.py
Writes dashboard/dashboard_data.csv for use in Power BI, Tableau, or Excel.
"""

import os
import sys
import pandas as pd

# Project root (parent of dashboard/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT = os.path.join(PROJECT_ROOT, "data", "preprocessed", "diabetic_preprocessed.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dashboard")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "dashboard_data.csv")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "readmit_30" not in df.columns:
        raise ValueError("Input CSV must contain 'readmit_30' column.")
    return df


def _aggregate_overall(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    readmissions = df["readmit_30"].sum()
    rate = (readmissions / total * 100) if total else 0
    return pd.DataFrame([{
        "metric_type": "overall",
        "dimension_value": "All",
        "encounter_count": total,
        "readmission_count": int(readmissions),
        "readmission_rate_pct": round(rate, 2),
    }])


def _aggregate_by_column(df: pd.DataFrame, col: str, metric_type: str) -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame()
    g = df.groupby(col, dropna=False).agg(
        encounter_count=("readmit_30", "count"),
        readmission_count=("readmit_30", "sum"),
    ).reset_index()
    g["readmission_rate_pct"] = (g["readmission_count"] / g["encounter_count"] * 100).round(2)
    g = g.rename(columns={col: "dimension_value"})
    g["metric_type"] = metric_type
    return g[["metric_type", "dimension_value", "encounter_count", "readmission_count", "readmission_rate_pct"]]


def _one_hot_to_breakdown(df: pd.DataFrame, prefix: str, metric_type: str) -> pd.DataFrame:
    """Derive breakdown from one-hot columns like race_AfricanAmerican, age_50-60), etc."""
    cols = [c for c in df.columns if c.startswith(prefix) and c != prefix]
    if not cols:
        return pd.DataFrame()
    # dimension_value = column name without prefix (e.g. AfricanAmerican, 50-60))
    rows = []
    for c in cols:
        label = c[len(prefix):].strip("_")
        subset = df[df[c] == 1]
        total = len(subset)
        readm = subset["readmit_30"].sum()
        rate = (readm / total * 100) if total else 0
        rows.append({
            "metric_type": metric_type,
            "dimension_value": label,
            "encounter_count": total,
            "readmission_count": int(readm),
            "readmission_rate_pct": round(rate, 2),
        })
    return pd.DataFrame(rows)


def _gender_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if "gender" not in df.columns:
        return pd.DataFrame()
    # May be 0/1 (encoded) or Male/Female
    g = df.copy()
    if g["gender"].dtype in ("int64", "float64"):
        g["gender_label"] = g["gender"].map({0: "Female", 1: "Male"})
    else:
        g["gender_label"] = g["gender"]
    return _aggregate_by_column(g, "gender_label", "by_gender")


def build_dashboard_data(df: pd.DataFrame) -> pd.DataFrame:
    """Build one long table: metric_type, dimension_value, encounter_count, readmission_count, readmission_rate_pct."""
    parts = [_aggregate_overall(df)]

    # By age: categorical column or one-hot
    if "age" in df.columns:
        parts.append(_aggregate_by_column(df, "age", "by_age"))
    else:
        parts.append(_one_hot_to_breakdown(df, "age_", "by_age"))

    # By gender
    parts.append(_gender_breakdown(df))

    # By race: categorical or one-hot
    if "race" in df.columns:
        parts.append(_aggregate_by_column(df, "race", "by_race"))
    else:
        parts.append(_one_hot_to_breakdown(df, "race_", "by_race"))

    # By medical specialty: categorical or one-hot
    if "medical_specialty" in df.columns:
        parts.append(_aggregate_by_column(df, "medical_specialty", "by_specialty"))
    else:
        parts.append(_one_hot_to_breakdown(df, "medical_specialty_", "by_specialty"))

    # By admission type if present (one-hot)
    adm_cols = [c for c in df.columns if c.startswith("admission_type_")]
    if adm_cols:
        parts.append(_one_hot_to_breakdown(df, "admission_type_", "by_admission_type"))
    elif "admission_type_id" in df.columns:
        parts.append(_aggregate_by_column(df.astype({"admission_type_id": str}), "admission_type_id", "by_admission_type"))

    # By primary diagnosis category if present (one-hot)
    diag_cols = [c for c in df.columns if c.startswith("diag_1_cat_")]
    if diag_cols:
        parts.append(_one_hot_to_breakdown(df, "diag_1_cat_", "by_primary_diagnosis"))

    combined = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    return combined


def main(input_path: str = None, output_path: str = None):
    input_path = input_path or DEFAULT_INPUT
    output_path = output_path or OUTPUT_CSV
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}")
        print("Run the data pipeline first: python src/run_data_pipeline.py")
        sys.exit(1)
    _ensure_output_dir()
    df = _load_data(input_path)
    out = build_dashboard_data(df)
    out.to_csv(output_path, index=False)
    print(f"Dashboard data saved: {output_path} ({len(out)} rows)")


if __name__ == "__main__":
    main()
