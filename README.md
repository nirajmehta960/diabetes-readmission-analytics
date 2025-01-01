# Predicting 30-Day Hospital Readmissions for Diabetes Patients

## Executive Summary

Hospital readmissions within 30 days cost the US healthcare system **~$41 billion annually**. Under the Hospital Readmissions Reduction Program (HRRP), hospitals face CMS penalties for excess readmissions.

This project analyzes **101,766 patient encounters** across **130 US hospitals** (1999–2008) to identify key readmission drivers and build a predictive model that flags high-risk diabetes patients at discharge.

> **Bottom line:** A predictive model targeting 500 high-risk patients per hospital could prevent ~100 readmissions annually, saving an estimated **$1.5M per hospital per year**.

---

## Key Findings

| #   | Finding                                         | Detail                                                                     |
| --- | ----------------------------------------------- | -------------------------------------------------------------------------- |
| 1   | **Prior inpatient visits** are the #1 predictor | Patients with 3+ prior visits have 25%+ readmission rate (vs. 9% baseline) |
| 2   | **HbA1c not tested** in 83% of encounters       | Mandating testing is a low-cost, high-impact intervention                  |
| 3   | **Medication complexity** matters               | Patients on 15+ medications have significantly higher risk                 |
| 4   | **Length of stay** signals severity             | Longer stays correlate with higher readmission probability                 |
| 5   | **Discharge destination** is critical           | Where patients go after discharge affects readmission risk                 |

## Model Performance

| Model               | AUC-ROC | Notes                                        |
| ------------------- | ------- | -------------------------------------------- |
| Logistic Regression | ~0.64   | Interpretable baseline (scaled features)     |
| Random Forest       | ~0.65   | Handles non-linearity, class_weight balanced |
| Gradient Boosting   | ~0.66   | Best performer in pipeline                   |

> **Note:** AUC-ROC of 0.63–0.67 is consistent with published benchmarks for this dataset (Strack et al., 2014). The model is used for risk stratification, not individual prediction; healthcare readmission is inherently challenging due to missing social determinants of health.

---

## Business Recommendations

| #   | Action                                                                       | Expected Impact               |
| --- | ---------------------------------------------------------------------------- | ----------------------------- |
| 1   | Flag patients with 1+ prior inpatient visits for enhanced discharge planning | Targets highest-risk group    |
| 2   | Mandate HbA1c testing for all diabetic admissions                            | Standard of care improvement  |
| 3   | 7-day post-discharge follow-up calls for flagged patients                    | Catch complications early     |
| 4   | Deploy real-time risk score at discharge                                     | Proactive resource allocation |
| 5   | Complex medication review at discharge for patients on 15+ medications       | Reduce polypharmacy risk      |

---

## Project Structure

```
healthcare-readmission-prediction/
|
├── README.md
├── requirements.txt
├── .gitignore
|
├── data/
|   ├── raw/                    # Original untouched dataset
|   |   ├── diabetic_data.csv
|   |   └── IDs_mapping.csv
|   ├── preprocessed/           # After Phase 2 (cleaning only)
|   |   └── diabetic_preprocessed.csv
|   ├── featured/               # After Phase 3 (feature engineering and encoding)
|   |   ├── diabetic_featured.csv
|   |   └── model_ready.csv
|   └── data_dictionary.md      # Column descriptions and mapping notes
|
├── notebooks/
|   ├── 01_data_profiling.ipynb       # Initial exploration and quality assessment
|   ├── 02_data_cleaning.ipynb        # Cleaning, deduplication, missing values
|   ├── 03_feature_engineering.ipynb  # New features, encoding, transformations
|   ├── 04_eda.ipynb                 # Exploratory analysis and visualizations
|   ├── 05_modeling.ipynb            # Model training, tuning, evaluation
|   └── 06_insights_recommendations.ipynb  # Business insights and impact analysis
|
├── sql/
|   ├── 01_create_tables.sql    # Load CSV into SQL database
|   ├── 02_data_profiling.sql   # Profiling queries
|   └── 03_validation_queries.sql  # Post-cleaning validation checks
|
├── src/
|   ├── __init__.py
|   ├── data_cleaning.py
|   ├── feature_engineering.py
|   ├── modeling.py
|   └── visualizations.py
|
├── dashboard/
|   ├── dashboard_mockup.png
|   ├── dashboard_data.csv
|   └── README.md
|
├── model/                  # Saved trained model artifacts (.pkl, .joblib) from 05_modeling
|
├── reports/
|   ├── project_report.pdf
|   ├── executive_summary.pdf
|   └── presentation.pptx
|
└── images/
    ├── feature_importance.png
    ├── confusion_matrix.png
    ├── roc_curve.png
    └── eda_charts/
```

---

## Tools & Technologies

| Category             | Tools                                                                |
| -------------------- | -------------------------------------------------------------------- |
| **Languages**        | Python, SQL                                                          |
| **Data Analysis**    | Pandas, NumPy, SciPy                                                 |
| **Machine Learning** | Scikit-learn (Logistic Regression, Random Forest, Gradient Boosting) |
| **Visualization**    | Matplotlib, Seaborn                                                  |
| **Database**         | SQLite (optional, for SQL profiling)                                 |
| **Environment**      | Jupyter Lab                                                          |

---

## How to Run This Project

If you want to reproduce the analysis or run the dashboard locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/nirajmehta/healthcare-readmission-analysis.git
cd healthcare-readmission-analysis
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the Data

1. Download the dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/296/diabetes+130-us-hospitals+for+years+1999-2008).
2. Unzip the file `diabetes+130-us-hospitals+for+years+1999-2008.zip`.
3. Place `diabetic_data.csv` and `IDs_mapping.csv` into the `data/raw/` directory.

### 5. Run the Analysis

**Option A: Run via Jupyter Notebooks (Recommended)**
Launch Jupyter Lab and run the notebooks in order. The pipeline is: raw data (Phase 1) to preprocessed (Phase 2) to featured/model-ready (Phase 3), then EDA, modeling, and insights.

```bash
jupyter lab
```

Run in order:

1. `notebooks/01_data_profiling.ipynb` — initial exploration and SQL profiling
2. `notebooks/02_data_cleaning.ipynb` — cleaning, deduplication; outputs `data/preprocessed/diabetic_preprocessed.csv`
3. `notebooks/03_feature_engineering.ipynb` — new features and encoding; outputs `data/featured/diabetic_featured.csv` and `data/featured/model_ready.csv`
4. `notebooks/04_eda.ipynb` — exploratory analysis and visualizations (uses preprocessed or featured data)
5. `notebooks/05_modeling.ipynb` — train/evaluate models; saves ROC and confusion matrix to `images/`; save trained models (e.g. via `joblib.dump`) to `model/`
6. `notebooks/06_insights_recommendations.ipynb` — hypothesis validation, risk tiers, financial impact, recommendation cards

**Option B: Run via Python scripts**
From the project root, run preprocessing and/or feature engineering with default paths (`data/raw/`, `data/preprocessed/`, `data/featured/`):

Run the full data pipeline (Phase 2 + Phase 3):

```bash
python src/run_data_pipeline.py
```

Run preprocessing only (Phase 2; writes `data/preprocessed/diabetic_preprocessed.csv`):

```bash
python src/data_cleaning.py
```

Run feature engineering only (Phase 3; reads preprocessed, writes `data/featured/diabetic_featured.csv` and `data/featured/model_ready.csv`):

```bash
python src/feature_engineering.py
```

### 6. Dashboard and Reports

- **Dashboard:** Aggregated data for Tableau/Power BI is prepared in the pipeline (Phase 7) and documented in `dashboard/README.md`. Export summary KPIs, readmission rates by group, and risk score distributions to `dashboard/`.
- **Reports:** Place `project_report.pdf`, `executive_summary.pdf`, and `presentation.pptx` in the `reports/` folder.
- **Images:** Model outputs (ROC curve, confusion matrix, feature importance) and EDA charts are saved under `images/` and `images/eda_charts/`.

---

## Data Source

**UCI Machine Learning Repository — Diabetes 130-US Hospitals (1999–2008)**

- 101,766 encounters | 50 features | 130 US hospitals
- [Dataset Link](https://archive.ics.uci.edu/dataset/296/diabetes+130-us-hospitals+for+years+1999-2008)
- License: CC BY 4.0
- Original paper: Strack, B. et al. (2014). "Impact of HbA1c measurement on hospital readmission rates"

---

## Estimated Cost Impact

```
Average cost per readmission:           $15,000
High-risk patients flagged per year:        500
Readmissions prevented (20% rate):          100
───────────────────────────────────────────────
Annual savings per hospital:         $1,500,000
```
