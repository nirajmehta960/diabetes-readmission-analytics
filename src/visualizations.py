"""
Plotting helper functions for EDA and model evaluation.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import RocCurveDisplay, confusion_matrix


def save_fig(fig, path: str, dpi: int = 150):
    """Save figure to path; create parent dirs if needed."""
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_roc_curves(results_dict, y_test, title: str = "ROC Curves - All Models", save_path: str = None):
    """Plot ROC curves for multiple models on one axes."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, res in results_dict.items():
        RocCurveDisplay.from_predictions(
            y_test, res["y_proba"], name=name, ax=ax
        )
    ax.set_title(title)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
    return fig


def plot_confusion_matrices(results_dict, y_test, save_path: str = None):
    """Plot 1x3 confusion matrices for each model."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, (name, res) in zip(axes, results_dict.items()):
        cm = confusion_matrix(y_test, res["y_pred"])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_title(f"{name}\nAUC={res['AUC-ROC']:.3f}")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
    return fig


def plot_feature_importance(importance_series, top_n: int = 15, title: str = "Top Features", save_path: str = None):
    """Horizontal bar chart of feature importance (e.g. from Random Forest)."""
    top = importance_series.head(top_n)
    fig, ax = plt.subplots(figsize=(10, 8))
    top.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title(title)
    ax.set_xlabel("Importance")
    ax.invert_yaxis()
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
    return fig


def target_distribution_bar(y_series, title: str = "Target distribution"):
    """Bar chart of target class counts."""
    fig, ax = plt.subplots(figsize=(6, 4))
    y_series.value_counts().plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Class")
    return fig


def readmission_rate_by_group(df, group_col: str, target_col: str = "readmit_30"):
    """Grouped bar or rate overlay by a categorical column."""
    rate = df.groupby(group_col)[target_col].agg(["mean", "count", "sum"])
    rate.columns = ["readmit_rate", "count", "readmits"]
    return rate


def generate_all_eda_charts(df, save_dir: str = "images/eda_charts"):
    """Generate and save all exploratory data analysis charts."""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Readmission Overview
    if 'readmit_30' in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(data=df, x='readmit_30', ax=ax, palette='Set2')
        ax.set_title("Target Variable Distribution (Readmit 30)")
        save_fig(fig, os.path.join(save_dir, "readmission_overview.png"))
        
    # 2. Missing Values (Dummy plot since preprocessed data has no/few missing)
    fig, ax = plt.subplots(figsize=(8, 4))
    missing = df.isnull().mean() * 100
    if missing.sum() > 0:
        missing[missing > 0].plot(kind='bar', ax=ax, color='salmon')
    else:
        ax.text(0.5, 0.5, "No Missing Values", ha='center', va='center')
    ax.set_title("Missing Values Percentage")
    save_fig(fig, os.path.join(save_dir, "missing_values.png"))

        
    # 5. Correlation Matrix
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        fig, ax = plt.subplots(figsize=(12, 10))
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, cmap='coolwarm', center=0, ax=ax)
        ax.set_title("Correlation Matrix")
        save_fig(fig, os.path.join(save_dir, "correlation_matrix.png"))
        
    # 6. Risk Factors
    if 'number_inpatient' in df.columns and 'readmit_30' in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=df, x='number_inpatient', y='readmit_30', errorbar=None, color='coral', ax=ax)
        ax.set_title("Readmission Rate by Prior Inpatient Visits")
        ax.set_xlim(-0.5, 5.5) # limit to interesting range
        save_fig(fig, os.path.join(save_dir, "risk_factors.png"))


def generate_cost_savings_chart(annual_savings: float, save_dir: str = "images/eda_charts"):
    """Generate a cost savings infographic-style chart."""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, f"Estimated Annual Cost Savings:\n${annual_savings:,.0f}", 
            ha='center', va='center', fontsize=24, color='forestgreen', weight='bold')
    ax.axis('off')
    save_fig(fig, os.path.join(save_dir, "cost_savings.png"))

