# Diccionario de datos normalizado

El CSV normalizado conserva el significado del archivo MIMP y usa nombres compatibles con PostgreSQL, Liquibase y Power BI.

| Campo | Tipo lógico | Descripción |
|---|---|---|
| `report_year` | entero | Año del reporte de información. |
| `report_period` | texto | Periodo reportado, por ejemplo `ENE - DIC` o `ENE - SET`. |
| `report_date` | fecha | Fecha de reporte convertida a ISO 8601 (`YYYY-MM-DD`). |
| `entity_code` | texto | Código de la entidad que reporta. |
| `program_name` | texto | Nombre del programa. |
| `line_code` | texto | Código de la línea de intervención. |
| `line_name` | texto | Nombre de la línea de intervención. |
| `service_code` | texto | Código del servicio. |
| `service_name` | texto | Nombre del servicio. |
| `ubigeo` | texto | Código UBIGEO de la ubicación del centro. Se conserva como texto para no perder ceros iniciales. |
| `department` | texto | Departamento del centro de atención. |
| `province` | texto | Provincia del centro de atención. |
| `district` | texto | Distrito del centro de atención. |
| `center_code` | texto | Código del centro. Cuando la fuente no lo informa, el modelo genera un identificador técnico `SIN-CODIGO-...` para no perder la fila. |
| `center_name` | texto | Nombre del centro. |
| `num_ca` | entero | Indicador/código numérico de centro de atención publicado por la fuente. |
| `total_nna` | entero | Total de NNA ingresados al Servicio de Protección Especial. |
| `male_nna` | entero | NNA hombres. |
| `female_nna` | entero | NNA mujeres. |
| `age_0_5_total` | entero | Total de NNA de 0 a 5 años. |
| `age_0_5_male` | entero | NNA hombres de 0 a 5 años. |
| `age_0_5_female` | entero | NNA mujeres de 0 a 5 años. |
| `age_6_11_total` | entero | Total de NNA de 6 a 11 años. |
| `age_6_11_male` | entero | NNA hombres de 6 a 11 años. |
| `age_6_11_female` | entero | NNA mujeres de 6 a 11 años. |
| `age_12_17_total` | entero | Total de NNA de 12 a 17 años. |
| `age_12_17_male` | entero | NNA hombres de 12 a 17 años. |
| `age_12_17_female` | entero | NNA mujeres de 12 a 17 años. |
| `age_18_plus_total` | entero | Total de personas de 18 años a más que aparece en el archivo fuente. |
| `age_18_plus_male` | entero | Hombres de 18 años a más. |
| `age_18_plus_female` | entero | Mujeres de 18 años a más. |
| `source_snapshot` | texto | Etiqueta del corte de descarga usado, actualmente `2025-09`. |

Los valores vacíos del origen se cargan como `NULL`. Las sumas de `total_nna` representan acumulaciones de filas reportadas; no deben interpretarse como personas únicas.
