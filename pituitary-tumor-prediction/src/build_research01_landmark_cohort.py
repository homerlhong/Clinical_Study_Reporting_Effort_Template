"""Build an auditable landmark cohort for research-01 strategy comparisons.

This creates treatment-strategy labels from dates. It does not estimate treatment
effects and must run only inside an approved data environment for real records.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _read(data_dir: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(data_dir / filename, dtype="string", keep_default_na=False).replace("", pd.NA)


def build_landmark_cohort(data_dir: Path, grace_days: int = 180) -> pd.DataFrame:
    """Return an eligible cohort with transparent early-strategy labels.

    Eligibility: postoperative residual plus early IGF-1 above the local ULN.
    The landmark is the first postoperative MRI / early biochemical assessment
    date available in the supplied early-postoperative table.
    """
    baseline = _read(data_dir, "patient_baseline.csv")[["patient_id", "index_surgery_date", "age_at_surgery_years"]]
    mri = _read(data_dir, "preop_mri.csv")[["patient_id", "tumor_volume_ml", "knosp_grade"]]
    early = _read(data_dir, "early_postop.csv")[[
        "patient_id", "postop_mri_date", "postoperative_residual", "residual_volume_ml",
        "residual_location", "early_igf1_date", "early_igf1_uln_ratio", "early_gh_value"
    ]]
    medication = _read(data_dir, "medication_events.csv")[["patient_id", "start_date", "medication_name"]]
    radiotherapy = _read(data_dir, "radiotherapy_events.csv")[["patient_id", "rt_actual_date", "rt_modality"]]

    frame = baseline.merge(mri, on="patient_id", how="left").merge(early, on="patient_id", how="left")
    for date_column in ["index_surgery_date", "postop_mri_date", "early_igf1_date"]:
        frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce")
    frame["landmark_date"] = frame[["postop_mri_date", "early_igf1_date"]].max(axis=1)
    frame["postoperative_residual"] = pd.to_numeric(frame["postoperative_residual"], errors="coerce")
    frame["early_igf1_uln_ratio"] = pd.to_numeric(frame["early_igf1_uln_ratio"], errors="coerce")
    frame["eligible_for_early_strategy_comparison"] = (
        frame["postoperative_residual"].eq(1)
        & frame["early_igf1_uln_ratio"].gt(1)
        & frame["landmark_date"].notna()
    )

    medication["start_date"] = pd.to_datetime(medication["start_date"], errors="coerce")
    radiotherapy["rt_actual_date"] = pd.to_datetime(radiotherapy["rt_actual_date"], errors="coerce")
    medication_first = medication.groupby("patient_id", as_index=False).agg(
        first_medication_date=("start_date", "min"), medication_name=("medication_name", "first")
    )
    rt_first = radiotherapy.groupby("patient_id", as_index=False).agg(
        first_rt_date=("rt_actual_date", "min"), rt_modality=("rt_modality", "first")
    )
    frame = frame.merge(medication_first, on="patient_id", how="left").merge(rt_first, on="patient_id", how="left")
    grace_end = frame["landmark_date"] + pd.to_timedelta(grace_days, unit="D")
    early_rt = frame["first_rt_date"].between(frame["landmark_date"], grace_end, inclusive="both")
    early_medication = frame["first_medication_date"].between(frame["landmark_date"], grace_end, inclusive="both")
    frame["strategy_assignment"] = "unassigned"
    frame.loc[frame["eligible_for_early_strategy_comparison"] & early_rt, "strategy_assignment"] = "early_SRS_GK"
    frame.loc[
        frame["eligible_for_early_strategy_comparison"] & ~early_rt & early_medication,
        "strategy_assignment",
    ] = "medical_first"
    frame["assignment_grace_days"] = grace_days
    frame["assignment_note"] = "Research strategy label; not a treatment recommendation."
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grace-days", type=int, default=180)
    args = parser.parse_args()
    cohort = build_landmark_cohort(args.data_dir, grace_days=args.grace_days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(args.output, index=False)
    assigned = cohort["strategy_assignment"].value_counts().to_dict()
    print(f"Wrote landmark cohort: {args.output}")
    print(f"Strategy assignments: {assigned}")


if __name__ == "__main__":
    main()
