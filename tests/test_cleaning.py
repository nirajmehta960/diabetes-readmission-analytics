import pandas as pd
from src.data_cleaning import map_icd9, binarize_target, drop_unusable_columns

def test_map_icd9():
    assert map_icd9(250) == "Diabetes"
    assert map_icd9(400) == "Circulatory"
    assert map_icd9(460) == "Respiratory"
    assert map_icd9("V20") == "Other"
    assert map_icd9("E900") == "Other"

def test_binarize_target():
    data = {"readmitted": ["<30", ">30", "NO", "<30"]}
    df = pd.DataFrame(data)
    df_out = binarize_target(df)
    assert "readmitted" not in df_out.columns
    assert "readmit_30" in df_out.columns
    assert list(df_out["readmit_30"]) == [1, 0, 0, 1]

def test_drop_unusable_columns():
    data = {
        "encounter_id": [1, 2],
        "weight": [None, None],
        "payer_code": ["A", "B"],
        "age": ["[0-10)", "[10-20)"]
    }
    df = pd.DataFrame(data)
    df_out = drop_unusable_columns(df)
    assert "weight" not in df_out.columns
    assert "payer_code" not in df_out.columns
    assert "encounter_id" in df_out.columns
    assert "age" in df_out.columns
