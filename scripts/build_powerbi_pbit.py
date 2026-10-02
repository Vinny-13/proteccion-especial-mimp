#!/usr/bin/env python3
"""Generate the Power BI PbixProj source and compile a refreshable PBIT."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = "ProteccionEspecial"
TABLE = "vw_admissions_flat"
RAW_CSV_URL = (
    "https://raw.githubusercontent.com/Vinny-13/"
    "proteccion-especial-mimp/main/data/proteccion_especial.csv"
)

# (name, Power BI type, M type, default aggregation)
COLUMNS = [
    ("report_year", "int64", "Int64.Type", "none"),
    ("report_period", "string", "Text.Type", "none"),
    ("report_date", "dateTime", "Date.Type", "none"),
    ("entity_code", "string", "Text.Type", "none"),
    ("program_name", "string", "Text.Type", "none"),
    ("line_code", "string", "Text.Type", "none"),
    ("line_name", "string", "Text.Type", "none"),
    ("service_code", "string", "Text.Type", "none"),
    ("service_name", "string", "Text.Type", "none"),
    ("ubigeo", "string", "Text.Type", "none"),
    ("department", "string", "Text.Type", "none"),
    ("province", "string", "Text.Type", "none"),
    ("district", "string", "Text.Type", "none"),
    ("center_code", "string", "Text.Type", "none"),
    ("center_name", "string", "Text.Type", "none"),
    ("num_ca", "int64", "Int64.Type", "sum"),
    ("total_nna", "int64", "Int64.Type", "sum"),
    ("male_nna", "int64", "Int64.Type", "sum"),
    ("female_nna", "int64", "Int64.Type", "sum"),
    ("age_0_5_total", "int64", "Int64.Type", "sum"),
    ("age_0_5_male", "int64", "Int64.Type", "sum"),
    ("age_0_5_female", "int64", "Int64.Type", "sum"),
    ("age_6_11_total", "int64", "Int64.Type", "sum"),
    ("age_6_11_male", "int64", "Int64.Type", "sum"),
    ("age_6_11_female", "int64", "Int64.Type", "sum"),
    ("age_12_17_total", "int64", "Int64.Type", "sum"),
    ("age_12_17_male", "int64", "Int64.Type", "sum"),
    ("age_12_17_female", "int64", "Int64.Type", "sum"),
    ("age_18_plus_total", "int64", "Int64.Type", "sum"),
    ("age_18_plus_male", "int64", "Int64.Type", "sum"),
    ("age_18_plus_female", "int64", "Int64.Type", "sum"),
    ("source_snapshot", "string", "Text.Type", "none"),
]

MEASURES = [
    ("Total NNA", f"SUM ( {TABLE}[total_nna] )", "#,0"),
    ("NNA hombres", f"SUM ( {TABLE}[male_nna] )", "#,0"),
    ("NNA mujeres", f"SUM ( {TABLE}[female_nna] )", "#,0"),
    ("% mujeres", "DIVIDE ( [NNA mujeres], [Total NNA], 0 )", "0.0%"),
    ("NNA 0-5", f"SUM ( {TABLE}[age_0_5_total] )", "#,0"),
    ("NNA 6-11", f"SUM ( {TABLE}[age_6_11_total] )", "#,0"),
    ("NNA 12-17", f"SUM ( {TABLE}[age_12_17_total] )", "#,0"),
    ("NNA 18+", f"SUM ( {TABLE}[age_18_plus_total] )", "#,0"),
    ("Centros", f"DISTINCTCOUNT ( {TABLE}[center_code] )", "#,0"),
    ("Registros", f"COUNTROWS ( {TABLE} )", "#,0"),
]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_ref(alias: str) -> dict:
    return {"SourceRef": {"Source": alias}}


def column_select(name: str) -> dict:
    return {
        "Column": {"Expression": source_ref("a"), "Property": name},
        "Name": f"{TABLE}.{name}",
        "NativeReferenceName": name,
    }


def measure_select(name: str) -> dict:
    return {
        "Measure": {"Expression": source_ref("a"), "Property": name},
        "Name": f"{TABLE}.{name}",
        "NativeReferenceName": name,
    }


def order_by(kind: str, name: str, direction: int = 2) -> dict:
    expression = {kind: {"Expression": source_ref("a"), "Property": name}}
    return {"Direction": direction, "Expression": expression}


def visual(
    name: str,
    visual_type: str,
    position: dict,
    selects: list[dict],
    projections: dict,
    sorting: list[dict] | None = None,
    title: str | None = None,
) -> dict:
    prototype = {
        "Version": 2,
        "From": [{"Name": "a", "Entity": TABLE, "Type": 0}],
        "Select": selects,
    }
    if sorting:
        prototype["OrderBy"] = sorting
    single = {
        "visualType": visual_type,
        "projections": projections,
        "prototypeQuery": prototype,
        "drillFilterOtherVisuals": True,
        "objects": {},
    }
    if title:
        escaped = "'" + title.replace("'", "''") + "'"
        single["vcObjects"] = {
            "title": [{"properties": {"text": {"expr": {"Literal": {"Value": escaped}}}}}]
        }
    return {
        "name": name,
        "layouts": [{"id": 0, "position": position}],
        "singleVisual": single,
    }


def add_visual(section: Path, folder: str, config: dict) -> None:
    destination = section / "visualContainers" / folder
    position = config["layouts"][0]["position"]
    write_json(
        destination / "visualContainer.json",
        {key: position[key] for key in ("height", "width", "x", "y", "z")},
    )
    write_json(destination / "config.json", config)
    write_json(destination / "filters.json", [])


def add_page(root: Path, ordinal: int, page_name: str, visuals: list[tuple[str, dict]]) -> None:
    section = root / "Report" / "sections" / f"{ordinal:03d}_{page_name}"
    write_json(
        section / "section.json",
        {
            "displayName": page_name,
            "displayOption": 1,
            "height": 720,
            "name": f"ReportSection{ordinal}",
            "ordinal": ordinal,
            "width": 1280,
        },
    )
    write_json(section / "config.json", {})
    write_json(section / "filters.json", [])
    for folder, config in visuals:
        add_visual(section, folder, config)


def write_root(root: Path) -> None:
    write_json(root / ".pbixproj.json", {"version": "1.0", "settings": {"model": {"serializationMode": "Default"}}})
    (root / "Version.txt").write_text("1.25", encoding="utf-8")
    write_json(
        root / "ReportMetadata.json",
        {
            "Version": 5,
            "AutoCreatedRelationships": [],
            "FileDescription": "MIMP Proteccion Especial",
            "CreatedFrom": "Cloud",
            "CreatedFromRelease": "2021.11",
        },
    )
    write_json(
        root / "ReportSettings.json",
        {
            "Version": 1,
            "ReportSettings": {},
            "QueriesSettings": {
                "TypeDetectionEnabled": True,
                "RelationshipImportEnabled": True,
                "RunBackgroundAnalysis": True,
                "Version": "2.81.5831.821",
            },
        },
    )
    write_json(
        root / "DiagramLayout.json",
        {
            "version": "1.1.0",
            "diagrams": [
                {
                    "ordinal": 0,
                    "scrollPosition": {"x": 0, "y": 0},
                    "nodes": [
                        {
                            "location": {"x": 40, "y": 40},
                            "nodeIndex": TABLE,
                            "size": {"height": 200, "width": 230},
                            "zIndex": 1,
                        }
                    ],
                    "name": "All tables",
                    "zoomValue": 100,
                    "pinKeyFieldsToTop": False,
                    "showExtraHeaderInfo": False,
                    "hideKeyFieldsWhenCollapsed": False,
                }
            ],
            "selectedDiagram": "All tables",
            "defaultDiagram": "All tables",
        },
    )


def write_model(root: Path) -> None:
    write_json(
        root / "Model" / "database.json",
        {
            "name": PROJECT,
            "compatibilityLevel": 1550,
            "model": {
                "culture": "es-PE",
                "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "sourceQueryCulture": "es-PE",
                "relationships": [],
                "annotations": [
                    {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
                    {"name": "PBIDesktopVersion", "value": "2.158.1177.0 (25.09)"},
                    {"name": "PBI_QueryOrder", "value": json.dumps([TABLE], separators=(",", ":"))},
                ],
            },
        },
    )
    table = root / "Model" / "tables" / TABLE
    write_json(table / "table.json", {"name": TABLE})
    for name, data_type, _m_type, summarize_by in COLUMNS:
        write_json(
            table / "columns" / f"{name}.json",
            {
                "name": name,
                "dataType": data_type,
                "sourceColumn": name,
                "summarizeBy": summarize_by,
                "annotations": [{"name": "SummarizationSetBy", "value": "User"}],
            },
        )
    for name, dax, format_string in MEASURES:
        folder = table / "measures"
        (folder / f"{name}.dax").parent.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.dax").write_text(dax + "\n", encoding="utf-8")
        (folder / f"{name}.xml").write_text(
            f'<Measure Name="{name}">\n  <FormatString>{format_string}</FormatString>\n</Measure>',
            encoding="utf-8",
        )

    transforms = ", ".join(f'{{"{name}", {m_type}}}' for name, _dtype, m_type, _sum in COLUMNS)
    query = (
        "let\n"
        f'    Source = Csv.Document(Web.Contents("{RAW_CSV_URL}"), '
        f"[Delimiter=\",\", Columns={len(COLUMNS)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n"
        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n"
        f"    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{{transforms}}})\n"
        "in\n"
        "    ChangedType\n"
    )
    query_folder = root / "Model" / "queries"
    query_folder.mkdir(parents=True, exist_ok=True)
    (query_folder / f"{TABLE}.m").write_text(query, encoding="utf-8")


def write_report(root: Path, theme_path: Path) -> None:
    theme_name = theme_path.name
    write_json(
        root / "Report" / "report.json",
        {
            "id": 0,
            "layoutOptimization": 0,
            "resourcePackages": [
                {
                    "resourcePackage": {
                        "disabled": False,
                        "name": "SharedResources",
                        "type": 2,
                        "items": [{"name": theme_path.stem, "path": f"BaseThemes/{theme_name}", "type": 202}],
                    }
                }
            ],
        },
    )
    write_json(
        root / "Report" / "config.json",
        {
            "version": "5.9",
            "themeCollection": {"baseTheme": {"name": theme_path.stem, "version": "5.10", "type": 2}},
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {"useNewFilterPaneExperience": True, "allowChangeFilterTypes": True},
        },
    )
    destination = root / "StaticResources" / "SharedResources" / "BaseThemes" / theme_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if theme_path.resolve() != destination.resolve():
        shutil.copyfile(theme_path, destination)

    total = measure_select("Total NNA")
    male = measure_select("NNA hombres")
    female = measure_select("NNA mujeres")
    women_pct = measure_select("% mujeres")
    age_0_5 = measure_select("NNA 0-5")
    age_6_11 = measure_select("NNA 6-11")
    age_12_17 = measure_select("NNA 12-17")
    age_18_plus = measure_select("NNA 18+")

    page_one = [
        ("00000_total_nna", visual("mimp_total_nna", "card", {"x": 40, "y": 30, "z": 0, "width": 270, "height": 105}, [total], {"Values": [{"queryRef": f"{TABLE}.Total NNA"}]}, title="Total NNA")),
        ("00001_hombres", visual("mimp_hombres", "card", {"x": 335, "y": 30, "z": 0, "width": 270, "height": 105}, [male], {"Values": [{"queryRef": f"{TABLE}.NNA hombres"}]}, title="NNA hombres")),
        ("00002_mujeres", visual("mimp_mujeres", "card", {"x": 630, "y": 30, "z": 0, "width": 270, "height": 105}, [female], {"Values": [{"queryRef": f"{TABLE}.NNA mujeres"}]}, title="NNA mujeres")),
        ("00003_pct_mujeres", visual("mimp_pct_mujeres", "card", {"x": 925, "y": 30, "z": 0, "width": 270, "height": 105}, [women_pct], {"Values": [{"queryRef": f"{TABLE}.% mujeres"}]}, title="% mujeres")),
        ("00004_tendencia_anual", visual("mimp_tendencia", "clusteredColumnChart", {"x": 40, "y": 165, "z": 1, "width": 585, "height": 265}, [column_select("report_year"), total], {"Category": [{"queryRef": f"{TABLE}.report_year"}], "Y": [{"queryRef": f"{TABLE}.Total NNA"}]}, [order_by("Column", "report_year", 1)], "Total NNA por año")),
        ("00005_departamentos", visual("mimp_departamentos", "clusteredBarChart", {"x": 655, "y": 165, "z": 1, "width": 585, "height": 265}, [column_select("department"), total], {"Category": [{"queryRef": f"{TABLE}.department"}], "Y": [{"queryRef": f"{TABLE}.Total NNA"}]}, [order_by("Measure", "Total NNA")], "Total NNA por departamento")),
        ("00006_filtro_anio", visual("mimp_filtro_anio", "slicer", {"x": 40, "y": 465, "z": 2, "width": 280, "height": 180}, [column_select("report_year")], {"Values": [{"queryRef": f"{TABLE}.report_year"}]}, title="Año reportado")),
        ("00007_filtro_departamento", visual("mimp_filtro_departamento", "slicer", {"x": 350, "y": 465, "z": 2, "width": 350, "height": 180}, [column_select("department")], {"Values": [{"queryRef": f"{TABLE}.department"}]}, title="Departamento")),
        ("00008_fuente", visual("mimp_fuente", "tableEx", {"x": 730, "y": 465, "z": 2, "width": 510, "height": 180}, [column_select("source_snapshot"), column_select("report_date"), measure_select("Registros")], {"Values": [{"queryRef": f"{TABLE}.source_snapshot"}, {"queryRef": f"{TABLE}.report_date"}, {"queryRef": f"{TABLE}.Registros"}]}, title="Corte de fuente")),
    ]

    page_two = [
        ("00000_sexo_departamento", visual("mimp_sexo_departamento", "clusteredColumnChart", {"x": 40, "y": 30, "z": 1, "width": 585, "height": 270}, [column_select("department"), male, female], {"Category": [{"queryRef": f"{TABLE}.department"}], "Y": [{"queryRef": f"{TABLE}.NNA hombres"}, {"queryRef": f"{TABLE}.NNA mujeres"}]}, [order_by("Measure", "NNA mujeres")], "NNA por sexo y departamento")),
        ("00001_edad_departamento", visual("mimp_edad_departamento", "clusteredBarChart", {"x": 655, "y": 30, "z": 1, "width": 585, "height": 270}, [column_select("department"), age_0_5, age_6_11, age_12_17, age_18_plus], {"Category": [{"queryRef": f"{TABLE}.department"}], "Y": [{"queryRef": f"{TABLE}.NNA 0-5"}, {"queryRef": f"{TABLE}.NNA 6-11"}, {"queryRef": f"{TABLE}.NNA 12-17"}, {"queryRef": f"{TABLE}.NNA 18+"}]}, [order_by("Measure", "NNA 12-17")], "NNA por grupo de edad")),
        ("00002_tendencia_sexo", visual("mimp_tendencia_sexo", "lineChart", {"x": 40, "y": 335, "z": 1, "width": 585, "height": 260}, [column_select("report_year"), male, female], {"Category": [{"queryRef": f"{TABLE}.report_year"}], "Y": [{"queryRef": f"{TABLE}.NNA hombres"}, {"queryRef": f"{TABLE}.NNA mujeres"}]}, [order_by("Column", "report_year", 1)], "Tendencia anual por sexo")),
        ("00003_detalle_centros", visual("mimp_detalle_centros", "tableEx", {"x": 655, "y": 335, "z": 1, "width": 585, "height": 260}, [column_select("center_name"), column_select("department"), column_select("province"), total, male, female], {"Values": [{"queryRef": f"{TABLE}.center_name"}, {"queryRef": f"{TABLE}.department"}, {"queryRef": f"{TABLE}.province"}, {"queryRef": f"{TABLE}.Total NNA"}, {"queryRef": f"{TABLE}.NNA hombres"}, {"queryRef": f"{TABLE}.NNA mujeres"}]}, [order_by("Measure", "Total NNA")], "Detalle por centro")),
        ("00004_filtro_anio", visual("mimp_filtro_anio_2", "slicer", {"x": 40, "y": 620, "z": 2, "width": 280, "height": 70}, [column_select("report_year")], {"Values": [{"queryRef": f"{TABLE}.report_year"}]}, title="Año reportado")),
        ("00005_filtro_departamento", visual("mimp_filtro_departamento_2", "slicer", {"x": 350, "y": 620, "z": 2, "width": 350, "height": 70}, [column_select("department")], {"Values": [{"queryRef": f"{TABLE}.department"}]}, title="Departamento")),
    ]
    add_page(root, 0, "Resumen ejecutivo", page_one)
    add_page(root, 1, "Perfil territorial y etario", page_two)


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: build_powerbi_pbit.py <directorio-pbixproj> <salida.pbit>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    pbit = Path(sys.argv[2]).resolve()
    theme = root / "StaticResources" / "SharedResources" / "BaseThemes" / "CY19SU12.json"
    if not theme.exists():
        print(f"No existe el tema Power BI: {theme}", file=sys.stderr)
        return 1
    write_root(root)
    write_model(root)
    write_report(root, theme)
    pbi_tools = Path(__file__).resolve().parents[3] / "work" / "pbi-tools" / "core" / "pbi-tools.core.exe"
    if not pbi_tools.exists():
        print(f"PbixProj generado en {root}; pbi-tools Core no está instalado localmente.")
        return 0
    result = subprocess.run([str(pbi_tools), "compile", str(root), str(pbit), "PBIT", "true"], check=False, text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

