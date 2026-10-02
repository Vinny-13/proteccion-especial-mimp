# Reporte Power BI

El reporte tiene dos páginas y está preparado como fuente reproducible de Power BI. La plantilla compilada es `ProteccionEspecial.pbit`; el archivo `ProteccionEspecial.pbix` se obtiene después de abrir la plantilla en Power BI Desktop, cargar/actualizar los datos y guardar el resultado.

## Artefactos

- `ProteccionEspecial.pbit`: plantilla compilada con pbi-tools Core.
- `pbixproj/`: modelo, consulta M, medidas, páginas y visuales en formato fuente.
- `../scripts/build_powerbi_pbit.py`: generador y compilador reproducible.
- `power-query.m` y `measures.dax`: referencia legible de la conexión y las medidas.

## Generar y convertir a PBIX

Desde la raíz del repositorio:

```powershell
python scripts/build_powerbi_pbit.py powerbi/pbixproj powerbi/ProteccionEspecial.pbit
```

Abre `ProteccionEspecial.pbit` con Power BI Desktop, elige **Cargar** cuando solicite actualizar la consulta pública, y luego guarda como `powerbi/ProteccionEspecial.pbix`. El PBIT no contiene credenciales ni datos embebidos; la consulta usa el CSV normalizado del repositorio.

## Conexión alternativa a PostgreSQL

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

El workflow `deploy.yml` importa `powerbi/ProteccionEspecial.pbix` mediante la API REST de Power BI en el workspace indicado por `PBI_WORKSPACE_ID`. La API de importación requiere un PBIX hidratado, no la plantilla PBIT.

## Publicación y permisos

El principal de servicio de Azure debe estar habilitado en el tenant de Power BI y ser miembro/administrador del workspace. La API utilizada requiere permiso `Dataset.ReadWrite.All`. Después de publicar, comparte el informe desde Power BI Service con la cuenta indicada en la consigna: `patcaudrosqeupt.pe`; si se trata de un correo, confirma con el docente el dominio y el carácter `@` faltante antes de enviar la invitación.
