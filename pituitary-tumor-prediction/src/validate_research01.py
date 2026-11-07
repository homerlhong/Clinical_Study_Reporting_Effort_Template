"""Structural QC for the GH PitNET research-01 templates.

This script validates structure and chronology only. It makes no clinical judgement.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "patient_baseline.csv": {"patient_id", "index_surgery_date", "age_at_surgery_years"},
    "preop_endocrine.csv": {"patient_id", "sample_date", "hormone_name", "hormone_value", "hormone_unit"},
    "preop_mri.csv": {"patient_id", "mri_date", "knosp_grade", "radiologic_cavernous_sinus_invasion"},
    "index_surgery_pathology.csv": {"patient_id", "surgery_date", "cell_lineage"},
    "early_postop.csv": {"patient_id", "postop_mri_date", "postoperative_residual"},
    "medication_events.csv": {"patient_id", "medication_name", "start_date"},
    "radiotherapy_events.csv": {"patient_id", "rt_actual_date", "rt_modality"},
    "reoperation_events.csv": {"patient_id", "reoperation_date"},
    "followup_events.csv": {"patient_id", "assessment_date"},
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype="string", keep_default_na=False).replace("", pd.NA)


def validate(data_dir: Path) -> list[str]:
    """Return validation errors; an empty list means the structural checks passed."""
    errors: list[str] = []
    tables: dict[str, pd.DataFrame] = {}
    for filename, required in REQUIRED_COLUMNS.items():
        path = data_dir / filename
        if not path.exists():
            errors.append(f"Missing required table: {filename}")
            continue
        table = _read_csv(path)
        tables[filename] = table
        missing = required - set(table.columns)
        if missing:
            errors.append(f"{filename}: missing columns {sorted(missing)}")
        if "patient_id" in table.columns and table["patient_id"].isna().any():
            errors.append(f"{filename}: patient_id contains missing values")

    baseline = tables.get("patient_baseline.csv")
    if baseline is None or "index_surgery_date" not in baseline.columns:
        return errors
    surgery_dates = pd.to_datetime(baseline.set_index("patient_id")["index_surgery_date"], errors="coerce")
    if surgery_dates.isna().any():
        errors.append("patient_baseline.csv: invalid or missing index_surgery_date")

    chronological_tables = {
        "early_postop.csv": "postop_mri_date",
        "radiotherapy_events.csv": "rt_actual_date",
        "reoperation_events.csv": "reoperation_date",
        "followup_events.csv": "assessment_date",
    }
    for filename, date_column in chronological_tables.items():
        table = tables.get(filename)
        if table is None or date_column not in table.columns:
            continue
        event_dates = pd.to_datetime(table[date_column], errors="coerce")
        if event_dates.isna().any() and len(table):
            errors.append(f"{filename}: invalid or missing {date_column}")
        indexed_surgery = table["patient_id"].map(surgery_dates)
        if (event_dates < indexed_surgery).fillna(False).any():
            errors.append(f"{filename}: contains events before index surgery")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.data_dir)
    if errors:
        raise SystemExit("QC failed:\n- " + "\n- ".join(errors))
    print("QC passed: template structure and checked chronology are valid.")


if __name__ == "__main__":
    main()
