#!/usr/bin/env python3
"""Build a commune-level bus-boardings panel from the DTPM Excel workbooks.

The source workbooks remain unchanged. Missing commune/day/time combinations are
left absent: whether they represent zero demand or missing coverage must be
verified before zero-filling the panel.

Run from the repository root with:
    uv run --with openpyxl --with pyxlsb python Etapa_02/codigo/build_panel.py
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, time
from pathlib import Path
from typing import Any, Iterable

from openpyxl import load_workbook
from pyxlsb import open_workbook


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "Datos" / "Fuentes"
SUBIDAS_DIR = DATA_DIR / "Subidas"
RESULTS_DIR = PROJECT_DIR / "Etapa_02" / "resultados"
DEFAULT_OUTPUT = RESULTS_DIR / "panel_demanda_bus.csv"
DEFAULT_MODEL_OUTPUT = RESULTS_DIR / "panel_demanda_bus_modelo.csv"
DEFAULT_REPORT = RESULTS_DIR / "panel_quality_report.json"

SOURCES = [
    ("2024-11", SUBIDAS_DIR / "Subida_Paradero_Estacion_2024.11.xlsb"),
    ("2025-04", SUBIDAS_DIR / "Subida_Paradero_Estacion_2025_04_v2.xlsb"),
    ("2025-11", SUBIDAS_DIR / "Subidas_Paradero_Estacion_2025.11.xlsx"),
    ("2026-04", SUBIDAS_DIR / "Subidas_Paradero_Estacion_2026.04_v3(1).xlsx"),
]

SHEET_PREFIX = "SUBIDAS_"


def ascii_key(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).strip().upper()


def header_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", ascii_key(value).lower())


def repair_mojibake(value: Any) -> str:
    """Repair the Latin-1/CP1252 decoding issue found in the Nov-2024 .xlsb."""
    text = str(value or "").strip()
    if not any(marker in text for marker in ("Ã", "Â", "\x80", "\x81", "\x8d", "\x91", "\x9d")):
        return text
    candidates = [text]
    for encoding in ("latin1", "cp1252"):
        try:
            candidates.append(text.encode(encoding).decode("utf-8"))
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    def score(candidate: str) -> int:
        return sum(candidate.count(marker) for marker in ("Ã", "Â", "\ufffd")) + sum(
            1 for char in candidate if 0x80 <= ord(char) <= 0x9F
        )
    return min(candidates, key=score)


def normalize_comuna(value: Any) -> str:
    value = unicodedata.normalize("NFC", repair_mojibake(value)).strip().upper()
    # This single alias is emitted as MAIPÊ by the legacy workbook conversion;
    # the official commune name and all other cuts use MAIPÚ.
    value = {"MAIPÊ": "MAIPÚ"}.get(value, value)
    if value in {"", "-", "SIN_COMUNA", "SIN COMUNA"}:
        return "SIN_COMUNA"
    return value


def normalize_day(value: Any) -> str:
    key = ascii_key(value)
    return {"SABADO": "SABADO", "SUNDAY": "DOMINGO"}.get(key, key)


def time_to_slot(value: Any) -> tuple[int | None, str | None]:
    """Return minutes after midnight and an error label, if not parseable."""
    if isinstance(value, datetime):
        minutes = value.hour * 60 + value.minute
    elif isinstance(value, time):
        minutes = value.hour * 60 + value.minute
    elif isinstance(value, (int, float)):
        # Excel stores a time as a fraction of one day.
        minutes = round(float(value) * 1440)
        if minutes == 1440:
            minutes = 0
    else:
        text = str(value or "").strip()
        if not text:
            return None, "missing_time"
        try:
            parsed = datetime.strptime(text[:8], "%H:%M:%S")
        except ValueError:
            try:
                parsed = datetime.strptime(text[:5], "%H:%M")
            except ValueError:
                return None, "invalid_time"
        minutes = parsed.hour * 60 + parsed.minute

    if minutes < 0 or minutes >= 1440:
        return None, "invalid_time"
    if minutes % 30:
        return None, "non_half_hour_time"
    return minutes, None


def to_number(value: Any) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result


def iter_xlsb(path: Path, sheet_name: str) -> Iterable[list[Any]]:
    with open_workbook(str(path)) as workbook:
        with workbook.get_sheet(sheet_name) as sheet:
            for row in sheet.rows():
                yield [cell.v for cell in row]


def iter_xlsx(path: Path, sheet_name: str) -> Iterable[tuple[Any, ...]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook[sheet_name]
        yield from sheet.iter_rows(values_only=True)
    finally:
        workbook.close()


def find_subidas_sheet(path: Path) -> str:
    if path.suffix.lower() == ".xlsb":
        with open_workbook(str(path)) as workbook:
            names = workbook.sheets
    else:
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            names = workbook.sheetnames
        finally:
            workbook.close()
    matches = [name for name in names if name.upper().startswith(SHEET_PREFIX)]
    if len(matches) != 1:
        raise ValueError(f"Expected one {SHEET_PREFIX} sheet in {path.name}; found {matches}")
    return matches[0]


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_DIR))
    except ValueError:
        return str(path)


def process_source(period: str, path: Path, aggregate: dict, report: dict,
                   read_path: Path | None = None) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Source workbook not found: {path}")
    workbook_path = read_path or path
    sheet_name = find_subidas_sheet(workbook_path)
    rows = (iter_xlsb(workbook_path, sheet_name) if workbook_path.suffix.lower() == ".xlsb"
            else iter_xlsx(workbook_path, sheet_name))
    header = next(rows, None)
    if not header:
        raise ValueError(f"Empty sheet {sheet_name} in {path.name}")

    indices = {header_key(name): index for index, name in enumerate(header) if name is not None}
    required = {"tipodia", "modo", "comuna", "mediahora", "subidaspromedio"}
    missing = required - indices.keys()
    if missing:
        raise ValueError(f"Missing columns in {path.name}: {sorted(missing)}; headers={header}")

    c = Counter()
    c["sheet"] = sheet_name
    for row in rows:
        c["rows_total"] += 1
        if len(row) <= max(indices[k] for k in required):
            c["short_rows"] += 1
            continue
        mode = ascii_key(row[indices["modo"]])
        if mode != "BUS":
            c["rows_non_bus"] += 1
            continue
        c["rows_bus"] += 1

        day = normalize_day(row[indices["tipodia"]])
        comuna = normalize_comuna(row[indices["comuna"]])
        minute, time_error = time_to_slot(row[indices["mediahora"]])
        target = to_number(row[indices["subidaspromedio"]])
        if not day:
            c["missing_day"] += 1
            continue
        if time_error:
            c[time_error] += 1
            continue
        if target is None:
            c["missing_or_invalid_target"] += 1
            continue
        if target < 0:
            c["negative_target"] += 1
            continue

        key = (period, comuna, day, minute)
        aggregate[key] += target
        c["rows_included"] += 1
        if target == 0:
            c["explicit_zero_rows"] += 1
        c[f"day:{day}"] += 1
        c[f"commune:{comuna}"] += 1

    report[period] = {
        "source": str(path.relative_to(PROJECT_DIR)),
        "sheet": sheet_name,
        "rows_total": c["rows_total"],
        "rows_bus": c["rows_bus"],
        "rows_non_bus": c["rows_non_bus"],
        "rows_included": c["rows_included"],
        "explicit_zero_rows": c["explicit_zero_rows"],
        "short_rows": c["short_rows"],
        "missing_day": c["missing_day"],
        "missing_time": c["missing_time"],
        "invalid_time": c["invalid_time"],
        "non_half_hour_time": c["non_half_hour_time"],
        "missing_or_invalid_target": c["missing_or_invalid_target"],
        "negative_target": c["negative_target"],
        "days": sorted(k.removeprefix("day:") for k in c if k.startswith("day:")),
        "communes": sorted(k.removeprefix("commune:") for k in c if k.startswith("commune:")),
    }
    print(f"{period}: {c['rows_included']:,} BUS rows included; "
          f"{len(report[period]['communes'])} communes; "
          f"days={report[period]['days']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Sparse commune panel with observed rows")
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_OUTPUT,
                        help="Dense model panel on communes present in every period")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    aggregate: defaultdict[tuple[str, str, str, int], float] = defaultdict(float)
    report: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="dtpm-panel-") as temp_dir:
        temp_dir_path = Path(temp_dir)
        for period, path in SOURCES:
            read_path = path
            if path.suffix.lower() == ".xlsb":
                libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
                if not libreoffice:
                    raise RuntimeError(
                        "LibreOffice is required to convert the two legacy .xlsb workbooks. "
                        "Install it or convert those files to .xlsx first."
                    )
                result = subprocess.run(
                    [libreoffice, "--headless", "--convert-to", "xlsx", "--outdir",
                     str(temp_dir_path), str(path)],
                    capture_output=True, text=True, check=False,
                )
                converted_path = temp_dir_path / f"{path.stem}.xlsx"
                if result.returncode != 0 or not converted_path.exists():
                    raise RuntimeError(
                        f"Could not convert {path.name} to xlsx: "
                        f"{result.stderr.strip() or result.stdout.strip()}"
                    )
                read_path = converted_path
            process_source(period, path, aggregate, report, read_path=read_path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        stream.write("periodo,comuna,tipo_dia,media_hora,subidas_promedio\n")
        for (period, comuna, day, minute), value in sorted(aggregate.items()):
            hh, mm = divmod(minute, 60)
            stream.write(f'"{period}","{comuna}","{day}","{hh:02d}:{mm:02d}",{value:.10g}\n')

    # Use only geographic entities present in every cut. SIN_COMUNA is not a
    # commune and is excluded from the commune-level forecasting panel.
    commune_sets = {
        period: {key[1] for key in aggregate if key[0] == period and key[1] != "SIN_COMUNA"}
        for period, _ in SOURCES
    }
    common_communes = set.intersection(*commune_sets.values())
    days = sorted({key[2] for key in aggregate})
    model_rows = 0
    zero_filled: Counter[str] = Counter()
    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    with args.model_output.open("w", encoding="utf-8", newline="") as stream:
        stream.write("periodo,comuna,tipo_dia,media_hora,subidas_promedio,relleno_cero\n")
        for period, _ in SOURCES:
            for comuna in sorted(common_communes):
                for day in days:
                    for minute in range(0, 1440, 30):
                        key = (period, comuna, day, minute)
                        is_filled = key not in aggregate
                        value = aggregate.get(key, 0.0)
                        hh, mm = divmod(minute, 60)
                        stream.write(
                            f'"{period}","{comuna}","{day}","{hh:02d}:{mm:02d}",'
                            f"{value:.10g},{int(is_filled)}\n"
                        )
                        model_rows += 1
                        zero_filled[period] += int(is_filled)

    # Coverage report keeps source coverage separate from model-panel zero filling.
    by_period: dict[str, dict[str, Any]] = {}
    for period, _ in SOURCES:
        keys = [key for key in aggregate if key[0] == period]
        by_period[period] = {
            "communes_in_source_including_sin_comuna": len({key[1] for key in keys}),
            "commune_day_slot_rows_observed": len(keys),
            "zero_filled_model_rows": zero_filled[period],
        }
    report["panel"] = {
        "observed_panel_output": display_path(args.output),
        "observed_panel_rows": len(aggregate),
        "model_panel_output": display_path(args.model_output),
        "model_panel_rows": model_rows,
        "common_communes_excluding_sin_comuna": sorted(common_communes),
        "model_panel_zero_fill": "Missing commune/day/slot rows are provisionally treated as zero; verify against DTPM export semantics.",
        "period_coverage": by_period,
        "note": "The model panel uses only communes present in all four cuts; the observed panel retains every reported commune.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPanel: {len(aggregate):,} rows -> {args.output}")
    print(f"Quality report -> {args.report}")


if __name__ == "__main__":
    main()
