# ETL Workshop 1 — Data Engineer

This project performs an end-to-end ETL pipeline over a dataset of 50,000 candidate applications.  
It extracts raw data, transforms it into a clean star-schema model, and loads it into a SQLite Data Warehouse.  
Finally, it generates key KPIs and visualizations.

## Project Structure
ETL_Workshop1/
├─ data/ # candidates.csv
├─ dw/ # schema.sql, kpis.sql, dw_hiring.db
├─ plots/ # Generated visualizations (.png)
├─ src/ # etl_load.py and plots.py
└─ README.md


## Requirements
- Python 3.10+
- Libraries: `pandas`, `matplotlib`

Install dependencies:
```bash
pip install pandas matplotlib

How to Run

1. Run ETL and create the DW
python src/etl_load.py --csv data/candidates.csv --db dw/dw_hiring.db

2. Generate charts
python src/plots.py --db dw/dw_hiring.db --out plots/

KPIs Included
Hires by technology
Hires by year
Hires by seniority
Hires by country over years (USA, Brazil, Colombia, Ecuador)
-Hire rate (%) by technology
-Average scores by seniority

Notes
The hired flag is defined as:
code_challenge_score >= 7 AND technical_interview_score >= 7

dim_candidate uses email as a unique key

date_id uses the format YYYYMMDD

Visuals use matplotlib only (no seaborn, no subplots)