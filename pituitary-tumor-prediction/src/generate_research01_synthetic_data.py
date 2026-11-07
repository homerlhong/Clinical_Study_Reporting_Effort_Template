"""Generate synthetic multi-table data to test research-01 pipelines.

The output is fictional and must never be interpreted as clinical evidence.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _date_series(start: str, offsets: np.ndarray) -> pd.Series:
    return pd.to_datetime(start) + pd.to_timedelta(offsets, unit="D")


def generate(output_dir: Path, n: int = 120, seed: int = 42) -> None:
    """Write research-01 compatible synthetic CSV tables to output_dir."""
    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    ids = [f"SYN-{i:04d}" for i in range(1, n + 1)]
    surgery_dates = _date_series("2017-01-01", rng.integers(0, 2000, n))
    age = rng.normal(49, 12, n).clip(18, 82).round(1)
    knosp = rng.choice([2, 3, 4], size=n, p=[0.15, 0.5, 0.35])
    preop_volume = rng.lognormal(1.2 + 0.25 * (knosp - 2), 0.45, n).round(2)
    residual_probability = 1 / (1 + np.exp(-(-1.0 + 0.9 * (knosp - 2))))
    residual = rng.binomial(1, residual_probability)
    residual_volume = (preop_volume * residual * rng.uniform(0.05, 0.55, n)).round(2)
    early_igf1 = (rng.normal(1.2, 0.45, n) + 0.25 * residual).clip(0.3, 3.2).round(2)

    pd.DataFrame({
        "patient_id": ids,
        "index_surgery_date": surgery_dates.date,
        "age_at_surgery_years": age,
        "sex_at_birth": rng.choice(["female", "male"], n),
        "acromegaly_diagnosis_basis": "clinical_biochemical_mri",
        "tumor_subtype": "GH_secreting",
        "familial_or_genetic_flag": rng.choice(["0", "1", "unknown"], n, p=[0.85, 0.03, 0.12]),
        "prior_pitnet_treatment": "0",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "patient_baseline.csv", index=False)

    preop_dates = surgery_dates - pd.to_timedelta(rng.integers(7, 90, n), unit="D")
    pd.DataFrame({
        "patient_id": ids,
        "sample_date": preop_dates.date,
        "hormone_name": "IGF-1",
        "hormone_value": (early_igf1 * 250).round(1),
        "hormone_unit": "ng/mL",
        "reference_lower": 80,
        "reference_upper": 250,
        "assay_platform": "synthetic_assay",
        "medication_state_at_sampling": "untreated",
        "igf1_uln_ratio": (early_igf1 + rng.uniform(0.4, 1.8, n)).round(2),
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "preop_endocrine.csv", index=False)

    pd.DataFrame({
        "patient_id": ids,
        "mri_date": preop_dates.date,
        "scanner_vendor": "synthetic_scanner",
        "field_strength_t": 3,
        "sequence_protocol": "contrast_T1",
        "max_diameter_mm": (preop_volume ** (1 / 3) * 12).round(1),
        "tumor_volume_ml": preop_volume,
        "knosp_grade": knosp,
        "radiologic_cavernous_sinus_invasion": 1,
        "invasion_confidence": rng.choice(["definite", "probable"], n, p=[0.8, 0.2]),
        "suprasellar_extension": rng.binomial(1, 0.55, n),
        "optic_chiasm_compression": rng.binomial(1, 0.2, n),
        "ica_encasement_or_contact": rng.choice(["contact", "partial_encasement"], n),
        "review_type": "synthetic_central_review",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "preop_mri.csv", index=False)

    pd.DataFrame({
        "patient_id": ids,
        "surgery_date": surgery_dates.date,
        "surgical_approach": "endoscopic_transsphenoidal",
        "operative_cavernous_sinus_involvement": 1,
        "extent_of_resection": np.where(residual == 1, "subtotal", "gross_total"),
        "residual_reason": np.where(residual == 1, "cavernous_sinus", pd.NA),
        "cell_lineage": "PIT1",
        "hormone_ihc_profile": "GH_positive",
        "granulation_pattern": rng.choice(["dense", "sparse", "unknown"], n, p=[0.4, 0.4, 0.2]),
        "ki67_percent": rng.uniform(0.2, 5.0, n).round(1),
        "mitotic_count": rng.integers(0, 4, n),
        "p53_ihc": rng.choice(["negative", "focal"], n, p=[0.8, 0.2]),
        "pathology_review_status": "synthetic_review",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "index_surgery_pathology.csv", index=False)

    postop_dates = surgery_dates + pd.to_timedelta(rng.integers(70, 150, n), unit="D")
    pd.DataFrame({
        "patient_id": ids,
        "postop_mri_date": postop_dates.date,
        "postoperative_residual": residual,
        "residual_volume_ml": residual_volume,
        "residual_max_diameter_mm": (residual_volume ** (1 / 3) * 12).round(1),
        "residual_location": np.where(residual == 1, "cavernous_sinus", "none"),
        "early_igf1_date": postop_dates.date,
        "early_igf1_uln_ratio": early_igf1,
        "early_gh_date": postop_dates.date,
        "early_gh_value": (early_igf1 * 1.5).round(2),
        "early_biochemical_status": np.where(early_igf1 <= 1, "controlled", "active"),
        "new_postop_axis_deficit": rng.choice(["none", "thyroid_axis"], n, p=[0.85, 0.15]),
        "postop_visual_status": rng.choice(["improved", "stable"], n, p=[0.25, 0.75]),
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "early_postop.csv", index=False)

    active = early_igf1 > 1
    med_start = postop_dates + pd.to_timedelta(rng.integers(1, 35, n), unit="D")
    pd.DataFrame({
        "patient_id": np.array(ids)[active],
        "medication_name": "synthetic_SSA",
        "start_date": med_start[active].date,
        "stop_date": pd.NA,
        "dose": 20,
        "dose_unit": "mg",
        "frequency": "every_28_days",
        "treatment_intent": "postoperative_control",
        "reason_for_change": pd.NA,
        "adherence_assessment": "unknown",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "medication_events.csv", index=False)

    rt = active & (residual == 1) & (rng.random(n) < 0.32)
    rt_dates = postop_dates + pd.to_timedelta(rng.integers(120, 800, n), unit="D")
    pd.DataFrame({
        "patient_id": np.array(ids)[rt],
        "rt_actual_date": rt_dates[rt].date,
        "rt_modality": "GK",
        "rt_indication": "persistent_biochemical_activity",
        "target_volume_ml": residual_volume[rt],
        "margin_dose_gy": 20,
        "fraction_count": 1,
        "optic_pathway_max_dose_gy": 6,
        "pituitary_stalk_or_normal_gland_dose": pd.NA,
        "distance_to_optic_apparatus_mm": 5,
        "concurrent_medication_state": "synthetic_SSA",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "radiotherapy_events.csv", index=False)

    reop = active & (residual == 1) & ~rt & (rng.random(n) < 0.15)
    reop_dates = postop_dates + pd.to_timedelta(rng.integers(180, 900, n), unit="D")
    pd.DataFrame({
        "patient_id": np.array(ids)[reop],
        "reoperation_date": reop_dates[reop].date,
        "reoperation_indication": "accessible_residual_with_activity",
        "pre_reoperation_mri_date": (reop_dates[reop] - pd.Timedelta(days=30)).date,
        "pre_reoperation_biochemical_status": "active",
        "reoperation_outcome": "synthetic_unknown",
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "reoperation_events.csv", index=False)

    followup_dates = surgery_dates + pd.to_timedelta(rng.integers(800, 1500, n), unit="D")
    events = active & (rng.random(n) < 0.23)
    pd.DataFrame({
        "patient_id": ids,
        "assessment_date": followup_dates.date,
        "mri_status": np.where(events, "confirmed_progression", "stable_residual"),
        "tumor_volume_ml": (residual_volume * np.where(events, 1.35, 0.9)).round(2),
        "igf1_uln_ratio": (early_igf1 * np.where(events, 1.15, 0.85)).round(2),
        "gh_value": (early_igf1 * np.where(events, 1.8, 0.9)).round(2),
        "gh_unit": "ng/mL",
        "biochemical_control_status": np.where(events, "active", "controlled"),
        "new_hypopituitarism": "none",
        "visual_or_cranial_nerve_event": "none",
        "patient_reported_outcome": pd.NA,
        "event_adjudication_status": np.where(events, "confirmed", "not_applicable"),
        "last_known_event_free_date": followup_dates.date,
        "lost_to_followup_reason": pd.NA,
        "missing_reason": pd.NA,
    }).to_csv(output_dir / "followup_events.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.output_dir, n=args.n, seed=args.seed)
    print(f"Wrote synthetic research-01 data to {args.output_dir}")


if __name__ == "__main__":
    main()
