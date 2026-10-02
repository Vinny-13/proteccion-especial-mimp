# Plataforma de datos MIMP: Protección Especial

Implementación de referencia para ingerir, modelar, automatizar y visualizar el dataset público **“Niñas, niños y adolescentes ingresados al Servicio de Protección Especial [MIMP]”**.

## 1. Dataset y alcance

- Fuente: [Plataforma Nacional de Datos Abiertos](https://www.datosabiertos.gob.pe/dataset/ni%C3%B1as-ni%C3%B1os-y-adolescentes-ingresados-al-servicio-de-protecci%C3%B3n-especial-mimp-0).
- Productor: Ministerio de la Mujer y Poblaciones Vulnerables (MIMP).
- Corte descargado: `2025-09`, archivo `1.3.1 BdD_Proteccion Especial_10.csv`.
- Licencia publicada: Open Data Commons Attribution License.
- Recuperación de referencia: `2026-10-01`.
- El indicador mide cantidades reportadas por año, servicio y centro; no contiene nombres de personas y sus totales no deben interpretarse como individuos únicos.

El corte normalizado contiene 203 filas, 13 años reportados (`2013`–`2025`), 26 centros y 25 departamentos. La suma de `total_nna` de las filas es 237 944; es una suma de reportes, no un conteo deduplicado de personas.

El detalle de cada campo se encuentra en [docs/diccionario-datos.md](docs/diccionario-datos.md). La metadata de la fuente está en [data/source-metadata.json](data/source-metadata.json).

## 2. Arquitectura de datos

1. El CSV se descarga desde la URL pública.
2. `scripts/normalize_dataset.py` resuelve codificación, nombres de columnas, fechas, códigos UBIGEO y campos vacíos.
3. Liquibase carga el CSV estable en `mimp.stg_proteccion_especial`.
4. La transformación llena `dim_geography`, `dim_service`, `dim_center` y `fact_admissions`.
5. Las vistas `mimp.vw_admissions_flat`, `mimp.vw_admissions_by_department` y `mimp.vw_admissions_by_age_sex` sirven a Power BI.

Diagrama editable: [docs/diagrama-er.mmd](docs/diagrama-er.mmd).

Los archivos SQL principales son:

- [db/changelog/001-schema.sql](db/changelog/001-schema.sql): staging, dimensiones, hechos e índices.
- [db/changelog/003-transform-data.sql](db/changelog/003-transform-data.sql): carga idempotente de dimensiones y hechos.
- [db/changelog/004-views.sql](db/changelog/004-views.sql): vistas analíticas.
- [db/changelog/db.changelog-master.yaml](db/changelog/db.changelog-master.yaml): changelog ejecutado por Liquibase.

También se incluyen wrappers para `psql` en [sql/](sql).

## 3. Infraestructura en Azure

Terraform crea:

- un Resource Group;
- un Azure Database for PostgreSQL Flexible Server 16, SKU `B_Standard_B1ms`;
- la base `mimp_proteccion`;
- una regla para servicios Azure y una regla temporal para GitHub Actions.

El servidor queda con acceso público para que el runner pueda ejecutar Liquibase. Para un entorno real se recomienda red privada/VNet, Private Endpoint y un runner autoalojado dentro de la red.

Diagrama editable: [docs/diagrama-despliegue.mmd](docs/diagrama-despliegue.mmd).

El workflow [infra.yml](.github/workflows/infra.yml) ejecuta `terraform plan` y `terraform apply`. Configura estas variables/secretos en GitHub:

| Nombre | Tipo | Uso |
|---|---|---|
| `AZURE_CLIENT_ID` | Secret | Principal de servicio usado por OIDC. |
| `AZURE_TENANT_ID` | Secret | Tenant de Azure. |
| `AZURE_SUBSCRIPTION_ID` | Secret | Suscripción de Azure. |
| `DB_ADMIN_PASSWORD` | Secret | Contraseña del administrador PostgreSQL. |
| `AZURE_RESOURCE_GROUP` | Variable | Opcional; por defecto `rg-mimp-proteccion`. |
| `AZURE_LOCATION` | Variable | Opcional; por defecto `eastus`. |
| `AZURE_DB_SERVER_NAME` | Variable | Obligatoria; nombre único global del servidor. |
| `DB_NAME` | Variable | Opcional; por defecto `mimp_proteccion`. |
| `DB_ADMIN_USERNAME` | Variable | Opcional; por defecto `mimpadmin`. |
| `DATASET_SNAPSHOT_LABEL` | Variable | Opcional; por defecto `2025-09`. |
| `TF_STATE_STORAGE_ACCOUNT` | Variable | Obligatoria; cuenta StorageV2 globalmente única para el estado remoto. |
| `TF_STATE_RESOURCE_GROUP` | Variable | Opcional; por defecto el mismo Resource Group. |
| `TF_STATE_CONTAINER` | Variable | Opcional; por defecto `terraform-state`. |
| `TF_STATE_KEY` | Variable | Opcional; por defecto `mimp-proteccion.tfstate`. |

## 4. Setup de base de datos

El workflow [setup.yml](.github/workflows/setup.yml) puede ejecutarse manualmente o al terminar correctamente `infra.yml`. Descarga y normaliza el dataset, agrega la IP temporal del runner al firewall, ejecuta `liquibase validate`, ejecuta `liquibase update` y retira la regla temporal.

Para una ejecución local:

```powershell
pwsh ./scripts/download_dataset.ps1
python ./scripts/normalize_dataset.py `
  --input ./data/source/proteccion_especial_raw.csv `
  --output ./data/proteccion_especial.csv `
  --snapshot-label 2025-09
```

Luego, con Liquibase y PostgreSQL disponibles:

```powershell
liquibase `
  --changelog-file=db/changelog/db.changelog-master.yaml `
  --changelog-parameters="dataFile=data/proteccion_especial.csv" `
  --url="jdbc:postgresql://SERVIDOR:5432/mimp_proteccion?sslmode=require" `
  --username=mimpadmin update
```

## 5. Power BI

La especificación y los archivos fuente están en [powerbi/README.md](powerbi/README.md), [powerbi/report-design.md](powerbi/report-design.md), [powerbi/power-query.m](powerbi/power-query.m) y [powerbi/measures.dax](powerbi/measures.dax). También se incluyen la plantilla compilada [powerbi/ProteccionEspecial.pbit](powerbi/ProteccionEspecial.pbit), el PBIX hidratado [powerbi/ProteccionEspecial.pbix](powerbi/ProteccionEspecial.pbix) y su fuente reproducible en [powerbi/pbixproj](powerbi/pbixproj).

El informe debe tener como mínimo:

- Página/dashboard 1: resumen ejecutivo con tarjetas, tendencia anual y ranking territorial.
- Página/dashboard 2: perfil territorial y etario con matriz, columnas por sexo/edad y detalle por centro.
- Filtro: `report_year`, más `department` en la vista territorial.

La plantilla PBIT se genera con `python scripts/build_powerbi_pbit.py powerbi/pbixproj powerbi/ProteccionEspecial.pbit`. El PBIX ya hidratado se encuentra en `powerbi/ProteccionEspecial.pbix` y es el archivo que consume el workflow de publicación.

## 6. Publicación

[deploy.yml](.github/workflows/deploy.yml) importa el PBIX al workspace mediante la API REST de Power BI. Requiere la misma autenticación OIDC de Azure, el principal de servicio habilitado en el tenant de Power BI, permiso `Dataset.ReadWrite.All` y la variable `PBI_WORKSPACE_ID`.

Después de una ejecución exitosa:

1. Comparte el reporte publicado con la cuenta indicada en la consigna: `patcaudrosqeupt.pe`. Si es una dirección de correo, valida el formato completo con el docente antes de invitarla.
2. Completa en este README el enlace del repositorio GitHub.
3. Completa el enlace del reporte publicado que devuelva Power BI Service.

**URL del repositorio:** <https://github.com/Vinny-13/proteccion-especial-mimp>

**URL del reporte publicado:** `PENDIENTE_DE_COMPLETAR`

## 7. Subir a GitHub

Desde la raíz de este proyecto:

```bash
git init
git add .
git commit -m "Implementa plataforma MIMP de protección especial"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

No se incluyen credenciales, estados de Terraform ni el CSV fuente bruto. El CSV normalizado se versiona para que el modelo sea auditable y reproducible.
