--liquibase formatted sql

--changeset mimp:003-transform-data
INSERT INTO mimp.dim_geography (ubigeo, department, province, district)
SELECT DISTINCT
    NULLIF(trim(ubigeo), ''),
    NULLIF(trim(department), ''),
    NULLIF(trim(province), ''),
    NULLIF(trim(district), '')
FROM mimp.stg_proteccion_especial
WHERE NULLIF(trim(ubigeo), '') IS NOT NULL
ON CONFLICT (ubigeo) DO UPDATE SET
    department = EXCLUDED.department,
    province = EXCLUDED.province,
    district = EXCLUDED.district;

INSERT INTO mimp.dim_service (
    entity_code, program_name, line_code, line_name,
    service_code, service_name
)
SELECT DISTINCT
    NULLIF(trim(entity_code), ''),
    NULLIF(trim(program_name), ''),
    NULLIF(trim(line_code), ''),
    NULLIF(trim(line_name), ''),
    NULLIF(trim(service_code), ''),
    NULLIF(trim(service_name), '')
FROM mimp.stg_proteccion_especial
WHERE NULLIF(trim(service_code), '') IS NOT NULL
ON CONFLICT (entity_code, line_code, service_code) DO UPDATE SET
    program_name = EXCLUDED.program_name,
    line_name = EXCLUDED.line_name,
    service_name = EXCLUDED.service_name;

INSERT INTO mimp.dim_center (center_code, center_name, num_ca, ubigeo, service_key)
SELECT DISTINCT
    COALESCE(
        NULLIF(trim(s.center_code), ''),
        'SIN-CODIGO-' || md5(concat_ws('|', s.center_name, s.ubigeo, s.service_code))
    ),
    NULLIF(trim(s.center_name), ''),
    NULLIF(trim(s.num_ca), '')::integer,
    NULLIF(trim(s.ubigeo), ''),
    ds.service_key
FROM mimp.stg_proteccion_especial s
JOIN mimp.dim_service ds
  ON ds.entity_code IS NOT DISTINCT FROM NULLIF(trim(s.entity_code), '')
 AND ds.line_code IS NOT DISTINCT FROM NULLIF(trim(s.line_code), '')
 AND ds.service_code IS NOT DISTINCT FROM NULLIF(trim(s.service_code), '')
ON CONFLICT (center_code, service_key) DO UPDATE SET
    center_name = EXCLUDED.center_name,
    num_ca = EXCLUDED.num_ca,
    ubigeo = EXCLUDED.ubigeo;

INSERT INTO mimp.fact_admissions (
    report_year, report_period, report_date, center_key,
    total_nna, male_nna, female_nna,
    age_0_5_total, age_0_5_male, age_0_5_female,
    age_6_11_total, age_6_11_male, age_6_11_female,
    age_12_17_total, age_12_17_male, age_12_17_female,
    age_18_plus_total, age_18_plus_male, age_18_plus_female,
    source_snapshot
)
SELECT
    NULLIF(trim(s.report_year), '')::integer,
    NULLIF(trim(s.report_period), ''),
    NULLIF(trim(s.report_date), '')::date,
    dc.center_key,
    NULLIF(trim(s.total_nna), '')::integer,
    NULLIF(trim(s.male_nna), '')::integer,
    NULLIF(trim(s.female_nna), '')::integer,
    NULLIF(trim(s.age_0_5_total), '')::integer,
    NULLIF(trim(s.age_0_5_male), '')::integer,
    NULLIF(trim(s.age_0_5_female), '')::integer,
    NULLIF(trim(s.age_6_11_total), '')::integer,
    NULLIF(trim(s.age_6_11_male), '')::integer,
    NULLIF(trim(s.age_6_11_female), '')::integer,
    NULLIF(trim(s.age_12_17_total), '')::integer,
    NULLIF(trim(s.age_12_17_male), '')::integer,
    NULLIF(trim(s.age_12_17_female), '')::integer,
    NULLIF(trim(s.age_18_plus_total), '')::integer,
    NULLIF(trim(s.age_18_plus_male), '')::integer,
    NULLIF(trim(s.age_18_plus_female), '')::integer,
    NULLIF(trim(s.source_snapshot), '' )
FROM mimp.stg_proteccion_especial s
JOIN mimp.dim_service ds
  ON ds.entity_code IS NOT DISTINCT FROM NULLIF(trim(s.entity_code), '')
 AND ds.line_code IS NOT DISTINCT FROM NULLIF(trim(s.line_code), '')
 AND ds.service_code IS NOT DISTINCT FROM NULLIF(trim(s.service_code), '')
JOIN mimp.dim_center dc
  ON dc.center_code = COALESCE(
      NULLIF(trim(s.center_code), ''),
      'SIN-CODIGO-' || md5(concat_ws('|', s.center_name, s.ubigeo, s.service_code))
  )
 AND dc.service_key = ds.service_key
WHERE NULLIF(trim(s.report_year), '') IS NOT NULL
  AND NULLIF(trim(s.report_date), '') IS NOT NULL
ON CONFLICT (report_year, report_date, center_key) DO UPDATE SET
    report_period = EXCLUDED.report_period,
    total_nna = EXCLUDED.total_nna,
    male_nna = EXCLUDED.male_nna,
    female_nna = EXCLUDED.female_nna,
    age_0_5_total = EXCLUDED.age_0_5_total,
    age_0_5_male = EXCLUDED.age_0_5_male,
    age_0_5_female = EXCLUDED.age_0_5_female,
    age_6_11_total = EXCLUDED.age_6_11_total,
    age_6_11_male = EXCLUDED.age_6_11_male,
    age_6_11_female = EXCLUDED.age_6_11_female,
    age_12_17_total = EXCLUDED.age_12_17_total,
    age_12_17_male = EXCLUDED.age_12_17_male,
    age_12_17_female = EXCLUDED.age_12_17_female,
    age_18_plus_total = EXCLUDED.age_18_plus_total,
    age_18_plus_male = EXCLUDED.age_18_plus_male,
    age_18_plus_female = EXCLUDED.age_18_plus_female,
    source_snapshot = EXCLUDED.source_snapshot,
    loaded_at = now();
