# Hiring DW — ER Diagram (Mermaid)

```mermaid
erDiagram
    dim_candidate {
        INTEGER candidate_id PK
        TEXT first_name
        TEXT last_name
        TEXT email 
    }

    dim_country {
        INTEGER country_id PK
        TEXT country_name
    }

    dim_date {
        INTEGER date_id PK  "YYYYMMDD"
        TEXT date
        INTEGER year
        INTEGER quarter
        INTEGER month
        INTEGER day
        INTEGER is_weekend
    }

    dim_seniority {
        INTEGER seniority_id PK
        TEXT seniority
    }

    dim_technology {
        INTEGER technology_id PK
        TEXT technology
    }

    fact_hiring {
        INTEGER fact_id PK
        INTEGER candidate_id FK
        INTEGER date_id FK
        INTEGER country_id FK
        INTEGER technology_id FK
        INTEGER seniority_id FK
        REAL years_experience
        REAL code_challenge_score
        REAL technical_interview_score
        INTEGER hired "0/1"
    }

    dim_candidate   ||--o{ fact_hiring : candidate_id
    dim_date        ||--o{ fact_hiring : date_id
    dim_country     ||--o{ fact_hiring : country_id
    dim_technology  ||--o{ fact_hiring : technology_id
    dim_seniority   ||--o{ fact_hiring : seniority_id
