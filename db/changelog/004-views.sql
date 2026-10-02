--liquibase formatted sql

--changeset mimp:004-views runOnChange:true
CREATE OR REPLACE VIEW mimp.vw_admissions_flat AS
SELECT
    f.admission_key,
    f.report_year,
    f.report_period,
    f.report_date,
    f.source_snapshot,
    c.center_code,
    c.center_name,
    c.num_ca,
    g.ubigeo,
    g.department,
    g.province,
    g.district,
    s.entity_code,
    s.program_name,
    s.line_code,
    s.line_name,
    s.service_code,
    s.service_name,
    f.total_nna,
    f.male_nna,
    f.female_nna,
    f.age_0_5_total,
    f.age_0_5_male,
    f.age_0_5_female,
    f.age_6_11_total,
    f.age_6_11_male,
    f.age_6_11_female,
    f.age_12_17_total,
    f.age_12_17_male,
    f.age_12_17_female,
    f.age_18_plus_total,
    f.age_18_plus_male,
    f.age_18_plus_female
FROM mimp.fact_admissions f
JOIN mimp.dim_center c ON c.center_key = f.center_key
JOIN mimp.dim_service s ON s.service_key = c.service_key
LEFT JOIN mimp.dim_geography g ON g.ubigeo = c.ubigeo;

CREATE OR REPLACE VIEW mimp.vw_admissions_by_department AS
SELECT
    report_year,
    report_date,
    department,
    SUM(total_nna) AS total_nna,
    SUM(male_nna) AS male_nna,
    SUM(female_nna) AS female_nna
FROM mimp.vw_admissions_flat
GROUP BY report_year, report_date, department;

CREATE OR REPLACE VIEW mimp.vw_admissions_by_age_sex AS
SELECT report_year, report_date, department, '0-5' AS age_band, 'Total' AS sex, age_0_5_total AS nna_count
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '0-5', 'Hombres', age_0_5_male
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '0-5', 'Mujeres', age_0_5_female
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '6-11', 'Total', age_6_11_total
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '6-11', 'Hombres', age_6_11_male
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '6-11', 'Mujeres', age_6_11_female
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '12-17', 'Total', age_12_17_total
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '12-17', 'Hombres', age_12_17_male
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '12-17', 'Mujeres', age_12_17_female
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '18+', 'Total', age_18_plus_total
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '18+', 'Hombres', age_18_plus_male
FROM mimp.vw_admissions_flat
UNION ALL
SELECT report_year, report_date, department, '18+', 'Mujeres', age_18_plus_female;
