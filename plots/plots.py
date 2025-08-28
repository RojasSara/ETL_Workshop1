#!/usr/bin/env python3
import os, argparse, sqlite3, pandas as pd, matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="dw/dw_hiring.db")
    parser.add_argument("--out", default="plots")
    return parser.parse_args()

def run_query(conn, sql):
    return pd.read_sql_query(sql, conn)

def save_bar(df, x, y, title, outpath, rotate=False):
    plt.figure()
    plt.bar(df[x], df[y])
    plt.title(title)
    if rotate:
        plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()

def save_lines(df, x, y_cols, title, outpath):
    plt.figure()
    for col in y_cols:
        plt.plot(df[x], df[col], label=col)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()

if __name__ == "__main__":
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    conn = sqlite3.connect(args.db)

    # 1. Hires by technology (Top 15)
    df1 = run_query(conn, """
        SELECT t.technology, COUNT(*) AS hires
        FROM fact_hiring f
        JOIN dim_technology t ON f.technology_id = t.technology_id
        WHERE f.hired = 1
        GROUP BY t.technology
        ORDER BY hires DESC
        LIMIT 15;
    """)
    save_bar(df1, "technology", "hires", "Hires by Technology (Top 15)",
             os.path.join(args.out, "hires_by_technology.png"), rotate=True)

    # 2. Hires by year
    df2 = run_query(conn, """
        SELECT d.year, COUNT(*) AS hires
        FROM fact_hiring f
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE f.hired = 1
        GROUP BY d.year
        ORDER BY d.year;
    """)
    save_bar(df2, "year", "hires", "Hires by Year",
             os.path.join(args.out, "hires_by_year.png"))

    # 3. Hires by seniority level
    df3 = run_query(conn, """
        SELECT s.seniority, COUNT(*) AS hires
        FROM fact_hiring f
        JOIN dim_seniority s ON f.seniority_id = s.seniority_id
        WHERE f.hired = 1
        GROUP BY s.seniority
        ORDER BY hires DESC;
    """)
    save_bar(df3, "seniority", "hires", "Hires by Seniority",
             os.path.join(args.out, "hires_by_seniority.png"), rotate=True)

    # 4. Hires by country over years (focused on 4 countries)
    df4 = run_query(conn, """
        SELECT d.year, c.country_name, COUNT(*) AS hires
        FROM fact_hiring f
        JOIN dim_date d ON f.date_id = d.date_id
        JOIN dim_country c ON f.country_id = c.country_id
        WHERE f.hired = 1
          AND c.country_name IN ('United States', 'USA', 'Brazil', 'Colombia', 'Ecuador')
        GROUP BY d.year, c.country_name
        ORDER BY d.year, c.country_name;
    """)
    pivot = df4.pivot_table(index="year", columns="country_name",
                            values="hires", fill_value=0).reset_index()
    ycols = [col for col in pivot.columns if col != "year"]
    save_lines(pivot, "year", ycols, "Hires by Country (Yearly)",
               os.path.join(args.out, "hires_by_country_over_years.png"))

    # 5. Hire rate (%) by technology
    df5 = run_query(conn, """
        SELECT t.technology,
               ROUND(100.0 * AVG(f.hired), 2) AS hire_rate_pct
        FROM fact_hiring f
        JOIN dim_technology t ON f.technology_id = t.technology_id
        GROUP BY t.technology
        ORDER BY hire_rate_pct DESC
        LIMIT 15;
    """)
    save_bar(df5, "technology", "hire_rate_pct", "Hire Rate (%) by Technology",
             os.path.join(args.out, "hire_rate_by_technology.png"), rotate=True)

    # 6. Average scores by seniority level
    df6 = run_query(conn, """
        SELECT s.seniority,
               ROUND(AVG(f.code_challenge_score), 2) AS avg_code_challenge,
               ROUND(AVG(f.technical_interview_score), 2) AS avg_technical_interview
        FROM fact_hiring f
        JOIN dim_seniority s ON f.seniority_id = s.seniority_id
        GROUP BY s.seniority
        ORDER BY avg_code_challenge DESC;
    """)
    plt.figure()
    plt.plot(df6["seniority"], df6["avg_code_challenge"], label="Code Challenge (avg)")
    plt.plot(df6["seniority"], df6["avg_technical_interview"], label="Technical Interview (avg)")
    plt.title("Average Scores by Seniority")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(args.out, "avg_scores_by_seniority.png"), dpi=140)
    plt.close()

    conn.close()
    print("Charts successfully generated in:", args.out)
