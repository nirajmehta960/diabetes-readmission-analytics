import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

from pathlib import Path

# 1. Configuration (Dynamically calculated for portability)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "diabetes.sqlite"
SAVE_DIR = PROJECT_ROOT / "images" / "sql_charts"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_connection():
    return sqlite3.connect(str(DB_PATH))

def save_plot(filename):
    path = os.path.join(SAVE_DIR, filename)
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"INFO: Saved: {path}")

# --- CHART 1: Readmission Risk by Age & Diagnosis ---
def plot_age_diag():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM mart_readmission_by_age_diag", conn)
    conn.close()

    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid")
    sns.barplot(data=df, x='age', y='readmit_rate_pct', hue='diag_1_category', palette='viridis')
    plt.title("Readmission Risk by Age and Diagnosis Category", fontsize=16, weight='bold', pad=20)
    plt.ylabel("Readmission Rate (%)")
    plt.legend(title="Diagnosis Category", bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot("01_readmission_age_diag.png")

# --- CHART 2: Top 10 Specialties by Readmission Rate ---
def plot_specialty():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM mart_readmission_by_specialty LIMIT 10", conn)
    conn.close()

    plt.figure(figsize=(12, 7))
    sns.barplot(data=df, x='readmit_rate_pct', y='medical_specialty', palette='magma')
    plt.title("Top 10 Specialties by 30-Day Readmission Rate", fontsize=16, weight='bold', pad=20)
    plt.xlabel("Readmission Rate (%)")
    plt.ylabel("Medical Specialty")
    save_plot("02_top_specialties.png")

# --- CHART 3: Readmission Trends by Utilization Tier ---
def plot_utilization():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM mart_high_utilizers", conn)
    conn.close()

    plt.figure(figsize=(10, 6))
    order = ["High Utilization", "Medium Utilization", "Low Utilization", "No Prior Visits"]
    sns.lineplot(data=df, x='utilization_tier', y='readmit_rate_pct', marker='o', sort=False, linewidth=3, color='crimson')
    plt.title("Readmission Rate Escalation by Utilization Tier", fontsize=16, weight='bold', pad=20)
    plt.ylabel("Readmission Rate (%)")
    plt.xticks(ticks=range(len(order)), labels=order)
    save_plot("03_utilization_trends.png")

# --- CHART 4: Average Length of Stay by Utilization ---
def plot_los_utilization():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM mart_high_utilizers", conn)
    conn.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='utilization_tier', y='avg_los_days', palette='Blues_d')
    plt.title("Avg length of Stay (Days) by Utilization Tier", fontsize=16, weight='bold', pad=20)
    plt.ylabel("Average Days in Hospital")
    save_plot("04_los_by_utilization.png")

# --- CHART 5: Core KPI Dashboard (Text-based Summary) ---
def plot_kpis():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM mart_readmission_kpis", conn)
    conn.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    
    kpi_text = (
        f"DATASET TOTALS & KPIs\n"
        f"----------------------------\n"
        f"Total Encounters: {int(df['total_encounters'][0]):,}\n"
        f"Readmissions (<30 days): {int(df['readmit_30_count'][0]):,}\n"
        f"Overall Readmission Rate: {df['readmit_30_rate_pct'][0]:.2f}%\n"
        f"Avg Time in Hospital: {df['avg_los_days'][0]:.2f} Days\n"
        f"Avg Medications Prescribed: {df['avg_num_medications'][0]:.2f}"
    )
    
    plt.text(0.5, 0.5, kpi_text, ha='center', va='center', fontsize=20, 
             bbox=dict(facecolor='ghostwhite', alpha=0.8, boxstyle='round,pad=1'))
    plt.title("Executive Summary (From SQL Mart)", fontsize=18, weight='bold', pad=20)
    save_plot("05_executive_summary.png")

if __name__ == "__main__":
    print("RUNNING: Starting SQL Mart Visualization...")
    plot_age_diag()
    plot_specialty()
    plot_utilization()
    plot_los_utilization()
    plot_kpis()
    print("DONE: All 5 charts generated successfully!")
