import pandas as pd
import numpy as np
from src.feature_engineering import (
    add_total_visits_prior,
    add_med_change_count,
    encode_medication_ordinal,
    encode_binary_categoricals,
)


def test_add_total_visits_prior():
    data = {
        "number_outpatient": [1, 0, 3],
        "number_inpatient": [2, 0, 1],
        "number_emergency": [0, 1, 2],
    }
    df = pd.DataFrame(data)
    df_out = add_total_visits_prior(df)
    assert "total_visits_prior" in df_out.columns
    assert list(df_out["total_visits_prior"]) == [3, 1, 6]


def test_add_med_change_count():
    data = {
        "metformin": ["No", "Steady", "Up"],
        "insulin": ["Steady", "No", "Down"],
        "glipizide": ["No", "No", "No"],
    }
    df = pd.DataFrame(data)
    df_out = add_med_change_count(df, medication_cols=["metformin", "insulin", "glipizide"])
    assert "med_change_count" in df_out.columns
    # Row 0: insulin=Steady (1 change), Row 1: none, Row 2: metformin=Up + insulin=Down (2 changes)
    assert list(df_out["med_change_count"]) == [1, 1, 2]


def test_encode_medication_ordinal():
    data = {"metformin": ["No", "Steady", "Up", "Down"]}
    df = pd.DataFrame(data)
    df_out = encode_medication_ordinal(df, medication_cols=["metformin"])
    assert list(df_out["metformin"]) == [0, 1, 2, 3]


def test_encode_binary_categoricals():
    data = {
        "change": ["Ch", "No", "Ch"],
        "diabetesMed": ["Yes", "No", "Yes"],
        "gender": ["Male", "Female", "Male"],
    }
    df = pd.DataFrame(data)
    df_out = encode_binary_categoricals(df)
    assert list(df_out["change"]) == [1, 0, 1]
    assert list(df_out["diabetesMed"]) == [1, 0, 1]
    assert list(df_out["gender"]) == [1, 0, 1]
