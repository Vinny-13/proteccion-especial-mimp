# Reporte Power BI

El archivo binario `ProteccionEspecial.pbix` debe guardarse en esta carpeta después de construirlo en Power BI Desktop. El repositorio deja preparada la conexión, el modelo lógico, las medidas DAX y el diseño requerido; la creación del PBIX y su publicación requieren una cuenta de Power BI con acceso al workspace.

## Conexión

1. En Power BI Desktop instala/activa el conector PostgreSQL.
2. Crea los parámetros `pServer` y `pDatabase`.
3. Usa el contenido de `power-query.m` para importar `mimp.vw_admissions_flat`. Duplica la consulta y cambia `Item="vw_admissions_flat"` por `Item="vw_admissions_by_age_sex"` para la segunda vista.
4. Relaciona ambas consultas por `report_year`, `report_date` y `department`, o usa únicamente la vista plana para un modelo inicial.
5. Agrega las medidas de `measures.dax`.

## Dos páginas/dashboard propuestos

### 1. Resumen ejecutivo

- Tarjetas: `Total NNA`, `NNA hombres`, `NNA mujeres`, `% mujeres`.
- Línea: `Total NNA` por `report_year`.
- Barras: `Total NNA` por `department`.
- Segmentadores: `report_year`, `department` y `service_name`.

### 2. Perfil territorial y etario

- Matriz: `department` × `age_band`, con `NNA por edad`.
- Columnas apiladas: `age_band` por `sex`.
- Tabla de detalle: centro, provincia, distrito, servicio y total.
- Filtro obligatorio del informe: `report_year` o `department`.

Guarda el archivo como `powerbi/ProteccionEspecial.pbix`. El workflow `deploy.yml` lo importa mediante la API REST de Power BI en el workspace indicado por la variable `PBI_WORKSPACE_ID`.

## Publicación y permisos

El principal de servicio de Azure debe estar habilitado en el tenant de Power BI y ser miembro/administrador del workspace. La API utilizada requiere permiso `Dataset.ReadWrite.All`. Después de publicar, comparte el informe desde Power BI Service con la cuenta indicada en la consigna: `patcaudrosqeupt.pe`; si se trata de un correo, confirma con el docente el dominio y el carácter `@` faltante antes de enviar la invitación.
