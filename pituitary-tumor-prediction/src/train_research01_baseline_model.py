"""Train a research-only 3-year baseline model for study-01 data.

This code is an auditable prototype. It must not be used for patient care.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "age_at_surgery_years",
    "tumor_volume_ml",
    "knosp_grade",
    "postoperative_residual",
    "residual_volume_ml",
    "early_igf1_uln_ratio",
    "early_gh_value",
    "ki67_percent",
]


def _read(data_dir: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(data_dir / filename, dtype="string", keep_default_na=False).replace("", pd.NA)


def build_model_frame(data_dir: Path) -> pd.DataFrame:
    """Create an eligible 3-year landmark frame from research-01 event tables."""
    baseline = _read(data_dir, "patient_baseline.csv")[["patient_id", "index_surgery_date", "age_at_surgery_years"]]
    mri = _read(data_dir, "preop_mri.csv")[["patient_id", "tumor_volume_ml", "knosp_grade"]]
    pathology = _read(data_dir, "index_surgery_pathology.csv")[["patient_id", "ki67_percent"]]
    early = _read(data_dir, "early_postop.csv")[[
        "patient_id", "postoperative_residual", "residual_volume_ml", "early_igf1_uln_ratio", "early_gh_value"
    ]]
    followup = _read(data_dir, "followup_events.csv")[["patient_id", "assessment_date", "mri_status"]]
    frame = baseline.merge(mri, on="patient_id", how="left").merge(pathology, on="patient_id", how="left")
    frame = frame.merge(early, on="patient_id", how="left").merge(followup, on="patient_id", how="left")
    surgery_date = pd.to_datetime(frame["index_surgery_date"], errors="coerce")
    assessment_date = pd.to_datetime(frame["assessment_date"], errors="coerce")
    followup_days = (assessment_date - surgery_date).dt.days
    progression = frame["mri_status"].eq("confirmed_progression")
    eligible = (followup_days >= 3 * 365.25) | (progression & (followup_days <= 3 * 365.25))
    frame = frame.loc[eligible].copy()
    frame["progression_or_retreatment_3y"] = (progression.loc[eligible] & (followup_days.loc[eligible] <= 3 * 365.25)).astype(int)
    return frame


def train(data_dir: Path) -> dict[str, float | int | str]:
    """Fit cross-validated baseline logistic regression and return aggregate metrics."""
    frame = build_model_frame(data_dir)
    x = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = frame["progression_or_retreatment_3y"]
    if len(frame) < 20 or y.nunique() < 2:
        raise ValueError("Insufficient eligible records or outcome variation for baseline modelling.")
    minority_count = int(y.value_counts().min())
    n_splits = min(5, minority_count)
    if n_splits < 2:
        raise ValueError("At least two outcome events in each cross-validation setup are required.")
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=1000, solver="liblinear"),
    )
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    probabilities = cross_val_predict(model, x, y, cv=cv, method="predict_proba")[:, 1]
    return {
        "data_status": "research prototype; not clinically valid",
        "eligible_patients": int(len(frame)),
        "three_year_events": int(y.sum()),
        "cross_validation_folds": n_splits,
        "cross_validated_auc": float(roc_auc_score(y, probabilities)),
        "cross_validated_brier_score": float(brier_score_loss(y, probabilities)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = train(args.data_dir)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
