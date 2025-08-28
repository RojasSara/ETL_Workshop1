-- 1) Hires by technology
SELECT t.technology, COUNT(*) AS hires
FROM fact_hiring f
JOIN dim_technology t ON f.technology_id = t.technology_id
WHERE f.hired = 1
GROUP BY t.technology
ORDER BY hires DESC;

-- 2) Hires by year
SELECT d.year, COUNT(*) AS hires
FROM fact_hiring f
JOIN dim_date d ON f.date_id = d.date_id
WHERE f.hired = 1
GROUP BY d.year
ORDER BY d.year;

-- 3) Hires by seniority
SELECT s.seniority, COUNT(*) AS hires
FROM fact_hiring f
JOIN dim_seniority s ON f.seniority_id = s.seniority_id
WHERE f.hired = 1
GROUP BY s.seniority
ORDER BY hires DESC;

-- 4) Hires by country over years (focused: USA, Brazil, Colombia, Ecuador)
SELECT d.year, c.country_name, COUNT(*) AS hires
FROM fact_hiring f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_country c ON f.country_id = c.country_id
WHERE f.hired = 1
  AND c.country_name IN ('United States', 'USA', 'Brazil', 'Colombia', 'Ecuador')
GROUP BY d.year, c.country_name
ORDER BY d.year, hires DESC;

-- 5) Hire rate (%) by technology  (custom KPI)
SELECT t.technology,
       ROUND(100.0 * AVG(f.hired), 2) AS hire_rate_pct
FROM fact_hiring f
JOIN dim_technology t ON f.technology_id = t.technology_id
GROUP BY t.technology
ORDER BY hire_rate_pct DESC;

-- 6) Average scores by seniority  (custom KPI)
SELECT s.seniority,
       ROUND(AVG(f.code_challenge_score), 2) AS avg_code_challenge,
       ROUND(AVG(f.technical_interview_score), 2) AS avg_technical_interview
FROM fact_hiring f
JOIN dim_seniority s ON f.seniority_id = s.seniority_id
GROUP BY s.seniority
ORDER BY avg_code_challenge DESC;
