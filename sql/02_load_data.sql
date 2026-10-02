-- Ejecutar desde la raíz del repositorio con psql, después de 01_create_tables.sql.
\set ON_ERROR_STOP on
TRUNCATE TABLE mimp.stg_proteccion_especial;
\copy mimp.stg_proteccion_especial FROM 'data/proteccion_especial.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ENCODING 'UTF8');
\i db/changelog/003-transform-data.sql
\i db/changelog/004-views.sql
