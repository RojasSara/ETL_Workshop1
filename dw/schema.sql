PRAGMA foreign_keys = ON;

-- Dimensions
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,            -- YYYYMMDD
    date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_country (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_technology (
    technology_id INTEGER PRIMARY KEY AUTOINCREMENT,
    technology TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_seniority (
    seniority_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seniority TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_candidate (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE
);

-- Fact
CREATE TABLE IF NOT EXISTS fact_hiring (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    technology_id INTEGER NOT NULL,
    seniority_id INTEGER NOT NULL,
    years_experience REAL,
    code_challenge_score REAL,
    technical_interview_score REAL,
    hired INTEGER NOT NULL CHECK (hired IN (0,1)),
    FOREIGN KEY (candidate_id) REFERENCES dim_candidate(candidate_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id),
    FOREIGN KEY (technology_id) REFERENCES dim_technology(technology_id),
    FOREIGN KEY (seniority_id) REFERENCES dim_seniority(seniority_id)
);
