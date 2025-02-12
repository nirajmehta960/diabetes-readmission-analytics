import pandas as pd
import numpy as np
from src.modeling import (
    prepare_train_test,
    scale_numeric,
    get_default_models,
    get_best_model_name,
)


def _make_dummy_df(n=200):
    """Create a minimal model-ready dataframe for testing."""
    rng = np.random.RandomState(42)
    df = pd.DataFrame({
        "time_in_hospital": rng.randint(1, 14, n),
        "num_lab_procedures": rng.randint(1, 100, n),
        "num_medications": rng.randint(1, 40, n),
        "number_inpatient": rng.randint(0, 5, n),
        "number_diagnoses": rng.randint(1, 16, n),
        "readmit_30": rng.choice([0, 1], n, p=[0.88, 0.12]),
    })
    return df


def test_prepare_train_test_shapes():
    df = _make_dummy_df(200)
    X_train, X_test, y_train, y_test = prepare_train_test(df, test_size=0.2)
    assert len(X_train) == 160
    assert len(X_test) == 40
    assert len(y_train) == 160
    assert len(y_test) == 40
    assert "readmit_30" not in X_train.columns


def test_prepare_train_test_stratification():
    df = _make_dummy_df(500)
    _, _, y_train, y_test = prepare_train_test(df, test_size=0.2)
    # Stratification should keep class proportions similar
    train_rate = y_train.mean()
    test_rate = y_test.mean()
    assert abs(train_rate - test_rate) < 0.05


def test_scale_numeric():
    df = _make_dummy_df(100)
    X_train, X_test, _, _ = prepare_train_test(df, test_size=0.2)
    cols = ["time_in_hospital", "num_lab_procedures"]
    X_train_s, X_test_s, scaler = scale_numeric(X_train, X_test, numeric_cols=cols)
    # Scaled train columns should have ~zero mean
    assert abs(X_train_s["time_in_hospital"].mean()) < 0.1
    # Scaler should be fitted
    assert scaler is not None


def test_get_default_models():
    models = get_default_models()
    assert "Logistic Regression" in models
    assert "Random Forest" in models
    assert "Gradient Boosting" in models
    assert len(models) == 3


def test_get_best_model_name():
    results = {
        "Model A": {"AUC-ROC": 0.70, "F1": 0.40},
        "Model B": {"AUC-ROC": 0.65, "F1": 0.50},
        "Model C": {"AUC-ROC": 0.72, "F1": 0.35},
    }
    assert get_best_model_name(results, metric="AUC-ROC") == "Model C"
    assert get_best_model_name(results, metric="F1") == "Model B"
