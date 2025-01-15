"""
Model training and evaluation utilities for 30-day readmission prediction.
Train/test split, scaling, train Logistic Regression, Random Forest, Gradient Boosting; metrics and plots.
When run as a script: loads model_ready.csv, trains all models, saves the best model and scaler to model/.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    confusion_matrix,
    RocCurveDisplay,
    recall_score,
    precision_score,
    f1_score,
)


DEFAULT_NUMERIC_COLS = [
    "time_in_hospital", "num_lab_procedures", "num_procedures",
    "num_medications", "number_outpatient", "number_inpatient",
    "number_emergency", "number_diagnoses", "total_visits_prior",
    "med_change_count",
]


def prepare_train_test(
    df: pd.DataFrame,
    target_col: str = "readmit_30",
    test_size: float = 0.2,
    random_state: int = 42,
):
    """Split into X, y and train/test with stratification."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )


def scale_numeric(X_train, X_test, numeric_cols: list = None):
    """StandardScaler fit on train, transform train and test."""
    cols = numeric_cols or [c for c in DEFAULT_NUMERIC_COLS if c in X_train.columns]
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[cols] = scaler.fit_transform(X_train[cols])
    X_test_scaled[cols] = scaler.transform(X_test[cols])
    return X_train_scaled, X_test_scaled, scaler


def get_default_models():
    """Return dict of name -> sklearn model instance."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, class_weight="balanced",
            random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42
        ),
    }


def train_and_evaluate(models, X_train, X_test, y_train, y_test, use_scaled_for_lr=True,
                       X_train_scaled=None, X_test_scaled=None):
    """
    Train each model and compute AUC, recall, precision, F1; return results dict
    with y_pred and y_proba for each model.
    """
    results = {}
    for name, model in models.items():
        if name == "Logistic Regression" and use_scaled_for_lr and X_train_scaled is not None:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_proba)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        results[name] = {
            "AUC-ROC": auc, "Recall": recall, "Precision": precision, "F1": f1,
            "y_pred": y_pred, "y_proba": y_proba,
        }
    return results


def get_best_model_name(results: dict, metric: str = "AUC-ROC"):
    """Return the model name with highest value for the given metric."""
    return max(results, key=lambda k: results[k][metric])


def get_feature_importances(model, feature_names):
    """Return a pandas Series of feature importances (for tree-based models)."""
    return pd.Series(model.feature_importances_, index=feature_names).sort_values(ascending=False)


# Default path for model-ready data (project root relative to this file)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_READY_PATH = os.path.join(_PROJECT_ROOT, "data", "featured", "model_ready.csv")
DEFAULT_MODEL_DIR = os.path.join(_PROJECT_ROOT, "model")


def run_training_pipeline(
    data_path: str = None,
    model_dir: str = None,
    save_all_models: bool = False,
):
    """
    Load model_ready.csv, train all models, save the best model and scaler to model/.
    If save_all_models is True, also save each of the three models separately.
    """
    data_path = data_path or DEFAULT_MODEL_READY_PATH
    model_dir = model_dir or DEFAULT_MODEL_DIR
    os.makedirs(model_dir, exist_ok=True)

    df = pd.read_csv(data_path)
    X_train, X_test, y_train, y_test = prepare_train_test(df)
    X_train_scaled, X_test_scaled, scaler = scale_numeric(X_train, X_test)

    models = get_default_models()
    results = train_and_evaluate(
        models, X_train, X_test, y_train, y_test,
        use_scaled_for_lr=True, X_train_scaled=X_train_scaled, X_test_scaled=X_test_scaled,
    )
    best_name = get_best_model_name(results)
    best_model = models[best_name]

    # Save best model and scaler (scaler needed for LR at inference)
    best_path = os.path.join(model_dir, "best_model.pkl")
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    joblib.dump(best_model, best_path)
    joblib.dump(scaler, scaler_path)
    print(f"Best model ({best_name}) saved to {best_path}")
    print(f"Scaler saved to {scaler_path}")

    if save_all_models:
        for name, model in models.items():
            safe_name = name.lower().replace(" ", "_") + ".pkl"
            path = os.path.join(model_dir, safe_name)
            joblib.dump(model, path)
            print(f"Saved {name} to {path}")

    return results, best_model, scaler


if __name__ == "__main__":
    results, best_model, scaler = run_training_pipeline()
    print("Training complete. Artifacts in model/")
    
    # Generate visualizations
    import sys
    sys.path.insert(0, _PROJECT_ROOT)
    from src.visualizations import plot_roc_curves, plot_confusion_matrices, plot_feature_importance
    df = pd.read_csv(DEFAULT_MODEL_READY_PATH)
    X_train, X_test, y_train, y_test = prepare_train_test(df)
    
    images_dir = os.path.join(_PROJECT_ROOT, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    plot_roc_curves(results, y_test, save_path=os.path.join(images_dir, "roc_curve.png"))
    plot_confusion_matrices(results, y_test, save_path=os.path.join(images_dir, "confusion_matrix.png"))
    
    best_name = get_best_model_name(results)
    if hasattr(best_model, "feature_importances_"):
        importances = pd.Series(best_model.feature_importances_, index=X_train.columns).sort_values(ascending=False)
        plot_feature_importance(importances, save_path=os.path.join(images_dir, "feature_importance.png"))
    
    print("Visualizations saved to images/")
