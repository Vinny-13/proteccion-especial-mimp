#!/usr/bin/env python3
"""Normalize the MIMP semicolon-delimited CSV to the project staging format.

The public source has changed encoding and the number of age columns between
snapshots. The first 16 fields are stable, and the remaining fields are
mapped by position so that the loader remains reproducible.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from datetime import datetime
from pathlib import Path


OUTPUT_COLUMNS = [
    "report_year", "report_period", "report_date", "entity_code",
    "program_name", "line_code", "line_name", "service_code",
    "service_name", "ubigeo", "department", "province", "district",
    "center_code", "center_name", "num_ca", "total_nna", "male_nna",
    "female_nna", "age_0_5_total", "age_0_5_male", "age_0_5_female",
    "age_6_11_total", "age_6_11_male", "age_6_11_female",
    "age_12_17_total", "age_12_17_male", "age_12_17_female",
    "age_18_plus_total", "age_18_plus_male", "age_18_plus_female",
    "source_snapshot",
]


def read_source(path: Path) -> tuple[list[str], list[list[str]], str]:
    raw = path.read_bytes()
    errors: list[str] = []
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            reader = csv.reader(io.StringIO(text), delimiter=";")
            header = next(reader)
            rows = list(reader)
            if len(header) >= 28 and not any("\ufffd" in cell for cell in header):
                return header, rows, encoding
        except (UnicodeDecodeError, StopIteration) as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError("No se pudo decodificar el CSV fuente: " + "; ".join(errors))


def clean_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


def clean_int(value: str | None) -> str:
    value = clean_text(value)
    if not value:
        return ""
    return re.sub(r"[^0-9-]", "", value)


def parse_date(value: str | None) -> str:
    value = clean_text(value)
    if not value:
        return ""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Fecha no reconocida: {value!r}")


def normalize_rows(rows: list[list[str]], snapshot: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()

    for line_number, raw_row in enumerate(rows, start=2):
        row = raw_row + [""] * max(0, 31 - len(raw_row))
        if not any(clean_text(value) for value in row):
            continue
        if len(row) < 16:
            raise ValueError(f"Fila {line_number} tiene menos de 16 columnas")

        values = {
            "report_year": clean_int(row[0]),
            "report_period": clean_text(row[1]),
            "report_date": parse_date(row[2]),
            "entity_code": clean_text(row[3]),
            "program_name": clean_text(row[4]),
            "line_code": clean_text(row[5]),
            "line_name": clean_text(row[6]),
            "service_code": clean_text(row[7]),
            "service_name": clean_text(row[8]),
            "ubigeo": clean_text(row[9]).zfill(6),
            "department": clean_text(row[10]),
            "province": clean_text(row[11]),
            "district": clean_text(row[12]),
            "center_code": clean_text(row[13]),
            "center_name": clean_text(row[14]),
            "num_ca": clean_int(row[15]),
        }

        measure_names = OUTPUT_COLUMNS[16:-1]
        for index, name in enumerate(measure_names, start=16):
            values[name] = clean_int(row[index])
        values["source_snapshot"] = snapshot

        # A snapshot can contain repeated rows after a portal update. Keep one
        # record per report/date/service/center and make the choice stable.
        key = (
            values["report_year"], values["report_date"],
            values["entity_code"], values["line_code"],
            values["service_code"], values["center_code"],
        )
        if key in seen:
            continue
        seen.add(key)
        normalized.append(values)

    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--snapshot-label", required=True)
    args = parser.parse_args()

    header, rows, encoding = read_source(args.input)
    if len(header) < 28:
        raise ValueError(f"Se esperaban al menos 28 columnas; se encontraron {len(header)}")

    records = normalize_rows(rows, args.snapshot_label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    print(
        f"Normalizadas {len(records)} filas desde {args.input.name} "
        f"(encoding={encoding}) hacia {args.output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
