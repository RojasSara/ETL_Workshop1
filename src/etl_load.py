#!/usr/bin/env python3
import os, argparse, pandas as pd, sqlite3

# Read schema DDL from file
SCHEMA_SQL = open("dw/schema.sql", "r", encoding="utf-8").read()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/candidates.csv")
    parser.add_argument("--db",  default="dw/dw_hiring.db")
    return parser.parse_args()

def build_dw(csv_path, db_path):
    print("[1/7] Reading CSV:", csv_path)
    # Your CSV uses ';' as delimiter
    df = pd.read_csv(csv_path, sep=";")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    print("[2/7] Normalizing data types")
    df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")
    for c in ["yoe", "code_challenge_score", "technical_interview_score"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Basic cleanup
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    for c in ["country", "technology", "seniority"]:
        df[c] = df[c].astype(str).str.strip()

    print("[3/7] Creating HIRED flag (rule: ≥7 on both scores)")
    df["hired"] = ((df["code_challenge_score"] >= 7) & (df["technical_interview_score"] >= 7)).astype(int)

    print("[4/7] Creating SQLite database:", db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)
    conn.commit()

    print("[5/7] Loading dimension tables")
    dates = df["application_date"].dropna().drop_duplicates().sort_values()
    dim_date = pd.DataFrame({
        "date": dates.dt.strftime("%Y-%m-%d"),
        "year": dates.dt.year,
        "quarter": dates.dt.quarter,
        "month": dates.dt.month,
        "day": dates.dt.day,
        "is_weekend": dates.dt.dayofweek.isin([5,6]).astype(int)
    })
    dim_date.insert(0, "date_id", dates.dt.strftime("%Y%m%d").astype(int).values)
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)

    pd.DataFrame({"country_name": sorted(df["country"].dropna().unique())}) \
      .to_sql("dim_country", conn, if_exists="append", index=False)

    pd.DataFrame({"technology": sorted(df["technology"].dropna().unique())}) \
      .to_sql("dim_technology", conn, if_exists="append", index=False)

    pd.DataFrame({"seniority": sorted(df["seniority"].dropna().unique())}) \
      .to_sql("dim_seniority", conn, if_exists="append", index=False)

    dim_candidate = (
        df.sort_values("email")
          .dropna(subset=["email"])
          .drop_duplicates(subset=["email"], keep="first")[["first_name","last_name","email"]]
    )
    dim_candidate.to_sql("dim_candidate", conn, if_exists="append", index=False)

    # Lookup dictionaries to map natural keys -> surrogate IDs
    def fetch_map(table, key_col, id_col):
        m = {}
        for row in conn.execute(f"SELECT {id_col}, {key_col} FROM {table}"):
            m[row[1]] = row[0]
        return m
    country_map   = fetch_map("dim_country",   "country_name", "country_id")
    tech_map      = fetch_map("dim_technology","technology",   "technology_id")
    seniority_map = fetch_map("dim_seniority", "seniority",    "seniority_id")
    email_to_candidate = {email: cid for cid, email in conn.execute("SELECT candidate_id, email FROM dim_candidate")}

    print("[6/7] Loading fact table")
    fact = df.copy()
    # Build date_id from date
    fact["date_id"] = fact["application_date"].dt.strftime("%Y%m%d").astype(float)
    fact = fact.dropna(subset=["date_id"])
    fact["date_id"] = fact["date_id"].astype(int)

    # Map natural keys to surrogate keys
    fact["country_id"]    = fact["country"].map(country_map)
    fact["technology_id"] = fact["technology"].map(tech_map)
    fact["seniority_id"]  = fact["seniority"].map(seniority_map)
    fact["candidate_id"]  = fact["email"].map(email_to_candidate)

    # Select and rename
    fact_cols = [
        "candidate_id","date_id","country_id","technology_id","seniority_id",
        "yoe","code_challenge_score","technical_interview_score","hired"
    ]
    fact_clean = fact[fact_cols].rename(columns={"yoe": "years_experience"})

    # Drop rows with missing foreign keys
    fact_clean = fact_clean.dropna(subset=["candidate_id","date_id","country_id","technology_id","seniority_id"])

    # Load fact
    fact_clean.to_sql("fact_hiring", conn, if_exists="append", index=False)

    print("[7/7] Validating row counts")
    counts = {}
    for t in ["dim_date","dim_country","dim_technology","dim_seniority","dim_candidate","fact_hiring"]:
        counts[t] = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {t}", conn)["n"].iat[0]

    conn.close()
    print("LOAD COMPLETE")
    print("ROW COUNTS:", counts)

if __name__ == "__main__":
    args = parse_args()
    build_dw(args.csv, args.db)
