# Datos de entrada

`proteccion_especial.csv` es la versión normalizada del corte publicado por el MIMP. El archivo original usa `;` como separador, mezcla codificaciones entre versiones y tiene encabezados con caracteres dañados; `scripts/normalize_dataset.py` transforma el corte público al formato estable usado por el staging de PostgreSQL.

Para actualizarlo localmente:

```powershell
pwsh ./scripts/download_dataset.ps1
python ./scripts/normalize_dataset.py `
  --input ./data/source/proteccion_especial_raw.csv `
  --output ./data/proteccion_especial.csv `
  --snapshot-label 2025-09
```

El archivo fuente descargado se mantiene fuera del control de versiones mediante `.gitignore`. El CSV normalizado sí puede versionarse para que Power BI y una ejecución local sean reproducibles.
