# ETL Workshop 1 — Hiring Data Warehouse

A complete ETL pipeline that ingests raw candidate applications, transforms and models them into a star-schema SQLite Data Warehouse, then produces KPIs and charts for analysis.

---

## Contents
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Dataset & Business Rules](#dataset--business-rules)
- [How to Run](#how-to-run)
- [KPIs](#kpis)
- [Charts](#charts)
- [SQL Views (Optional)](#sql-views-optional)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```mermaid
graph TD
  classDef fact fill:#FFF8E1,stroke:#FBC02D,stroke-width:2,color:#111;
  classDef dim  fill:#E3F2FD,stroke:#64B5F6,stroke-width:1,color:#111;
  classDef ghost fill:transparent,stroke:transparent;

  fact["fact_hiring<br/>PK: fact_id<br/>FKs: candidate_id, date_id, country_id, technology_id, seniority_id<br/><br/>years_experience, code_challenge_score, technical_interview_score, hired"]:::fact

  dim_candidate["dim_candidate<br/>PK: candidate_id<br/>first_name, last_name, email"]:::dim
  dim_date["dim_date<br/>PK: date_id (YYYYMMDD)<br/>date, year, quarter, month, day, is_weekend"]:::dim
  dim_country["dim_country<br/>PK: country_id<br/>country_name"]:::dim
  dim_technology["dim_technology<br/>PK: technology_id<br/>technology"]:::dim
  dim_seniority["dim_seniority<br/>PK: seniority_id<br/>seniority"]:::dim

  top(( )):::ghost --> dim_date
  left(( )):::ghost --> dim_candidate
  right(( )):::ghost --> dim_country
  right2(( )):::ghost --> dim_technology
  farRight(( )):::ghost --> dim_seniority

  dim_candidate -->|candidate_id| fact
  dim_date -->|date_id| fact
  dim_country -->|country_id| fact
  dim_technology -->|technology_id| fact
  dim_seniority -->|seniority_id| fact

## Structure

ETL_Workshop1/
├─ data/              # candidates.csv (input)
├─ dw/                # schema.sql, kpis.sql, dw_hiring.db (output)
├─ plots/             # Generated PNG charts
├─ src/               # etl_load.py, plots.py
├─ ERD.md             # Mermaid diagram (star layout)
└─ README.md

## Dataset & Business Rules

Source file: data/candidates.csv (semicolon ; as delimiter).

Required columns (case-insensitive; underscores added by ETL):

first_name, last_name, email, application_date, country, yoe,
seniority, technology, code_challenge_score, technical_interview_score

Hiring rule:

hired = 1 if code_challenge_score >= 7 and technical_interview_score >= 7; otherwise 0.

Keys:

dim_candidate.email is treated as a natural unique key during loading (first occurrence wins).

dim_date.date_id = YYYYMMDD.

## How to Run

From the project root:

Create the Data Warehouse:
python src/etl_load.py --csv data/candidates.csv --db dw/dw_hiring.db

Generate charts:
python src/plots.py --db dw/dw_hiring.db --out plots/

Explore KPIs in VS Code:
Install the “SQLite” extension (alexcvzz).

Add connection to dw/dw_hiring.db.
Open and run queries from dw/kpis.sql (select a single query block → Run Query).

## KPIs
#	KPI	Purpose
1	Hires by Technology	Top technologies by number of hires
2	Hires by Year	Hiring trend over time
3	Hires by Seniority	Which seniority levels are hired more
4	Hires by Country Over Years	Country trend focus (US/Brazil/Colombia/Ecuador)
5	Hire Rate (%) by Technology	Conversion by technology (custom KPI)
6	Average Scores by Seniority	Score profile by seniority (custom KPI)

## Troubleshooting
No data in tables: re-run ETL ensuring the CSV path and sep=";" are correct.
DB locked: close any DB viewer/editor tabs then rerun ETL.
Different column names: check preprocessing in etl_load.py where columns are normalized.
Plots not created: confirm matplotlib is installed and plots/ has write permissions.

Requirements
Python 3.10+
pip install -r requirements.txt (pandas, matplotlib)