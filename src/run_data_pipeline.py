"""
Run the full data pipeline: preprocessing (Phase 2) and feature engineering (Phase 3).
Saves outputs to data/preprocessed/ and data/featured/ using the same default paths
as when running data_cleaning or feature_engineering separately.
"""

import sys
import os

# Ensure project root is on path when run as script
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.data_cleaning import run_cleaning_pipeline, DEFAULT_PREPROCESSED_PATH
from src.feature_engineering import run_feature_engineering_pipeline, DEFAULT_FEATURED_PATH, DEFAULT_MODEL_READY_PATH


def run_pipeline(
    raw_path: str = None,
    ids_path: str = None,
    preprocessed_path: str = None,
    featured_path: str = None,
    model_ready_path: str = None,
):
    """
    Execute preprocessing and feature engineering in sequence.
    All path arguments are optional; defaults write to data/preprocessed/ and data/featured/.
    """
    # Phase 2: preprocessing -> data/preprocessed/diabetic_preprocessed.csv
    run_cleaning_pipeline(
        data_path=raw_path,
        ids_path=ids_path,
        save_path=preprocessed_path,
    )
    print(f"Phase 2 done: preprocessed data saved to {preprocessed_path or DEFAULT_PREPROCESSED_PATH}")

    # Phase 3: feature engineering -> data/featured/diabetic_featured.csv, model_ready.csv
    run_feature_engineering_pipeline(
        input_path=preprocessed_path,
        featured_path=featured_path,
        model_ready_path=model_ready_path,
    )
    print(f"Phase 3 done: featured data saved to {featured_path or DEFAULT_FEATURED_PATH}")
    print(f"Phase 3 done: model-ready data saved to {model_ready_path or DEFAULT_MODEL_READY_PATH}")


if __name__ == "__main__":
    run_pipeline()
    print("Data pipeline complete.")
