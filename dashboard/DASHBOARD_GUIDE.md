# End-to-End Guide: Building Your First BI Dashboard

This guide walks you through building a BI (Business Intelligence) dashboard for the Healthcare Readmission project from scratch. No prior dashboard experience assumed.

---

## 1. What Is a BI Dashboard?

A **BI dashboard** is a screen (or set of screens) that shows key metrics and charts so stakeholders can:

- See performance at a glance (e.g. readmission rate, high-risk count).
- Slice by dimensions (e.g. by age, race, admission type).
- Spot trends and outliers without opening raw data or code.

You build it in a **dashboard tool** (Power BI, Tableau, Excel, etc.) by connecting to **prepared data** and dragging fields onto charts.

---

## 2. Do You Need a Separate dashboard_data.csv?

**Yes.** You should use one or more **aggregated** dataset(s) for the dashboard, not the full 70,000+ row tables.

| Use full data (e.g. model_ready.csv)           | Use aggregated dashboard data                     |
| ---------------------------------------------- | ------------------------------------------------- |
| Slow to load in BI tools                       | Fast: hundreds or thousands of rows               |
| Hard to build simple “rate by group” charts    | Already summarized (e.g. readmission rate by age) |
| Risk of mistakes (wrong filters, double-count) | Clear, pre-calculated metrics                     |

So the flow is:

1. **Prepare dashboard data** in Python (this project: run the script below or the notebook step).
2. **Save CSV/Excel** into the `dashboard/` folder (e.g. `dashboard_data.csv` plus optional extra files).
3. **Connect** your BI tool to those files and build charts.

You can have:

- **One file** (`dashboard_data.csv`): several summary tables stacked or in one wide table (with a “dataset” or “metric_type” column to distinguish).
- **Several files**: e.g. `kpis.csv`, `readmission_by_demographics.csv`, `risk_by_specialty.csv` — each optimized for specific charts.

Both approaches are valid; starting with one `dashboard_data.csv` is simplest.

---

## 3. Overview: Steps to Build the Dashboard

| Step | What you do                                                                        |
| ---- | ---------------------------------------------------------------------------------- |
| 1    | **Prepare data** — Run the dashboard data script so CSVs appear in `dashboard/`.   |
| 2    | **Pick a tool** — Power BI Desktop (free), Tableau Public (free), or Excel.        |
| 3    | **Connect data** — Point the tool at your CSV (or Excel) file(s).                  |
| 4    | **Build visuals** — Add charts (bars, lines, KPIs) and filters.                    |
| 5    | **Share** — Save the file (Power BI .pbix, Tableau .twbx) or publish to the cloud. |

---

## 4. Step 1: Prepare Dashboard Data

We need **aggregated** numbers, not one row per patient. Examples:

- **KPIs**: Total encounters, overall readmission rate, count of high-risk patients.
- **By demographic**: Readmission rate and count by age, gender, race.
- **By admission/discharge**: Rate by admission type, discharge disposition.
- **By risk/specialty**: Readmission rate by medical specialty (e.g. top 10), or by risk tier.

A script is provided that reads your existing project data and writes dashboard-ready CSV(s) into `dashboard/`.

**How to run it (from project root, with venv activated):**

```bash
source venv/bin/activate
python dashboard/prepare_dashboard_data.py
```

This will create (or overwrite) in the `dashboard/` folder:

- **dashboard_data.csv** — Main file: KPIs, rates by age/gender/race, by admission type, by specialty, etc., in a format that’s easy to use in Power BI or Tableau.
- Optionally other files (e.g. one per theme) if the script is extended later.

**When to re-run:** Whenever you refresh the underlying data (e.g. after re-running the cleaning or feature-engineering pipeline), run this script again so the dashboard data is up to date.

---

## 5. Step 2: Choose a Dashboard Tool

Pick **one** to start. All can read CSV.

| Tool                 | Cost                    | Best for                                                               |
| -------------------- | ----------------------- | ---------------------------------------------------------------------- |
| **Power BI Desktop** | Free                    | Windows; very common in enterprises; good for sharing .pbix files.     |
| **Tableau Public**   | Free                    | Mac or Windows; public sharing on Tableau Public; strong visuals.      |
| **Excel**            | Often already installed | Simple tables and charts; no “dashboard” layout but fine for learning. |
| **Google Sheets**    | Free                    | Web; upload CSV, use charts and pivot tables; easy to share a link.    |

**Recommendation for first time:** Use **Power BI Desktop** (Windows) or **Tableau Public** (Mac/Windows). This guide’s concepts apply to both; only the clicks differ.

- Power BI: [Download Power BI Desktop](https://powerbi.microsoft.com/desktop/)
- Tableau: [Download Tableau Public](https://www.tableau.com/products/public/download)

---

## 6. Step 3: Connect Your Data

**Power BI Desktop**

1. Open Power BI Desktop.
2. **Get data** > **Text/CSV** (or **Excel** if you export to .xlsx).
3. Browse to your project’s `dashboard/dashboard_data.csv`.
4. Click **Load** (or **Transform data** if you want to clean in Power Query first).
5. Your table appears in the **Data** pane on the right.

**Tableau Public**

1. Open Tableau.
2. Under **Connect**, choose **Text file** and select `dashboard_data.csv`.
3. Drag the table to the canvas (“Sheet 1”).
4. You’ll see columns in the left sidebar.

**Excel**

1. **Data** > **From Text/CSV** and select `dashboard_data.csv`.
2. Load into a sheet. Use this sheet (or a pivot table from it) as the source for charts.

---

## 7. Step 4: Build Your First Charts

Think of the dashboard as a **one-page report** with:

- **Top**: 2–4 KPI cards (e.g. total encounters, readmission rate %, high-risk count).
- **Middle**: 2–3 charts (e.g. readmission rate by age, by gender, by admission type).
- **Bottom**: 1–2 deeper cuts (e.g. by medical specialty, by risk tier).

**Chart types that work well:**

| What you want to show                   | Chart type                         | Typical fields                        |
| --------------------------------------- | ---------------------------------- | ------------------------------------- |
| One number (e.g. readmission rate)      | KPI card / big number              | Single value or sum/avg.              |
| Rate or count by category (age, gender) | Bar chart (horizontal or vertical) | Category = axis, metric = bar length. |
| Compare a few groups                    | Bar chart or small table           | Group, count, rate.                   |
| Distribution (e.g. risk score)          | Histogram or bar chart             | Bins/categories, count.               |

**In Power BI**

- **Visualizations** pane: click **Card** for a KPI; **Clustered bar chart** for bars.
- Drag a column to **Axis** (category) and a metric column to **Values** (e.g. Sum or Average).
- Use **Slicers** to filter by a dimension (e.g. age).

**In Tableau**

- Drag a dimension to **Rows** or **Columns**, and a measure to the other shelf (e.g. **Rows** = SUM(Readmissions), **Columns** = Age).
- Choose **Show Me** > Bar chart (or other type).
- For a KPI: put one measure on **Text** in a simple table or use a “single value” view.

**Tips**

- Keep titles clear (e.g. “Readmission rate by age”).
- Use one main color for “bad” (e.g. high readmission) and another for “good” or neutral.
- Add a short description or footnote if you share with others.

---

## 8. Step 5: Save and Share

- **Power BI**: Save as `.pbix`. You can later publish to Power BI service to share with colleagues (requires an account).
- **Tableau Public**: Save to Tableau Public (free account). You get a link to a public view.
- **Excel**: Save the workbook; share the file or export charts as images/PDF.

---

## 9. Suggested Layout for This Project

A simple one-page layout could look like this:

```
+------------------+------------------+------------------+
|  Total encounters|  Readmission rate |  High-risk count |
+------------------+------------------+------------------+
|  Readmission rate by age (bar)  |  Readmission rate by gender (bar)  |
+------------------+------------------+------------------+
|  Readmission rate by admission type (bar)  |  Top specialties by volume (bar)  |
+------------------+------------------+------------------+
|  Optional: risk tier distribution or readmission by diagnosis category  |
+------------------+------------------+------------------+
```

The exact columns in `dashboard_data.csv` will match these (e.g. `age_group`, `readmission_rate`, `encounter_count`, `admission_type`, etc.). The script that creates `dashboard_data.csv` is designed so these charts are straightforward to build.

---

## 10. Checklist

- [ ] Run `python dashboard/prepare_dashboard_data.py` and confirm `dashboard/dashboard_data.csv` exists.
- [ ] Install Power BI Desktop or Tableau Public.
- [ ] Connect the tool to `dashboard_data.csv`.
- [ ] Create 2–4 KPI cards.
- [ ] Create at least 2–3 bar charts (e.g. by age, gender, admission type).
- [ ] Add filters/slicers if useful.
- [ ] Save the dashboard file (and re-run the script whenever underlying data changes).

---

## 11. Do You Need More Than One CSV?

- **Starting out:** One `dashboard_data.csv` with multiple “themes” (KPIs, demographics, admission, specialty) is enough. You can use the same file for different charts; some rows might be for “KPI” and others for “by age” or “by specialty.”
- **Later:** If the file gets large or you want clearer separation, you can split into e.g. `kpis.csv`, `readmission_by_demographics.csv`, `readmission_by_specialty.csv` and connect each to different sheets or data sources in the same dashboard. The same script can be extended to write multiple files.

The guide and script are set up so you can succeed with **just dashboard_data.csv** for your first dashboard.
