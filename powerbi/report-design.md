# Especificación de diseño del informe

## Modelo

La vista plana contiene una fila por combinación de año reportado, fecha de reporte, servicio y centro. La vista `vw_admissions_by_age_sex` está desnormalizada para facilitar el gráfico por grupo de edad y sexo.

## Reglas de lectura

- `Total NNA` representa el campo total publicado por el MIMP; no es un conteo de personas nominales.
- El año del reporte no necesariamente coincide con el año de la fecha de reporte.
- Los valores vacíos de edad se conservan como `BLANK()`; no deben convertirse en cero sin indicarlo en el tooltip.
- Los cortes históricos pueden ser actualizados por el MIMP; la etiqueta `source_snapshot` identifica la descarga usada.

## Filtro mínimo

En ambas páginas incluir el segmentador `report_year`, con selección múltiple activada. En la página territorial agregar también `department`.
