# Dashboard

This folder holds everything you need to build a BI dashboard for the Healthcare Readmission project.

## Contents

| Item | Purpose |
|------|---------|
| **DASHBOARD_GUIDE.md** | End-to-end guide: what a dashboard is, how to prepare data, which tool to use (Power BI / Tableau / Excel), and how to build and share it. Start here. |
| **prepare_dashboard_data.py** | Script that builds aggregated data from your project dataset and saves it here. |
| **dashboard_data.csv** | Aggregated file produced by the script. Use this in Power BI, Tableau, or Excel. |

## Quick start

1. Read **DASHBOARD_GUIDE.md** (full walkthrough).
2. From the project root (with venv activated), run:
   ```bash
   python dashboard/prepare_dashboard_data.py
   ```
3. Open **dashboard_data.csv** in your chosen tool and follow the guide to create KPI cards and charts.

You do need a separate **dashboard_data.csv** (or similar): the guide explains why and how to refresh it when your data changes.
