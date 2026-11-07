"""Create descriptive cohort and treatment-path summaries for research-01.

This module intentionally makes no causal or clinical-effectiveness claims.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _read(data_dir: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(data_dir / filename, dtype="string", keep_default_na=False).replace("", pd.NA)


def _date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def build_summary(data_dir: Path) -> str:
    baseline = _read(data_dir, "patient_baseline.csv")
    mri = _read(data_dir, "preop_mri.csv")
    early = _read(data_dir, "early_postop.csv")
    medication = _read(data_dir, "medication_events.csv")
    radiotherapy = _read(data_dir, "radiotherapy_events.csv")
    reoperation = _read(data_dir, "reoperation_events.csv")
    followup = _read(data_dir, "followup_events.csv")

    patient_ids = set(baseline["patient_id"].dropna())
    rt_ids = set(radiotherapy["patient_id"].dropna())
    reop_ids = set(reoperation["patient_id"].dropna())
    med_ids = set(medication["patient_id"].dropna())

    paths = []
    for patient_id in sorted(patient_ids):
        labels = ["surgery"]
        if patient_id in med_ids:
            labels.append("medication")
        if patient_id in rt_ids:
            labels.append("SRS/GK")
        if patient_id in reop_ids:
            labels.append("reoperation")
        paths.append(" → ".join(labels))
    path_counts = pd.Series(paths).value_counts()

    ages = pd.to_numeric(baseline["age_at_surgery_years"], errors="coerce")
    volumes = pd.to_numeric(mri["tumor_volume_ml"], errors="coerce")
    knosp = pd.to_numeric(mri["knosp_grade"], errors="coerce")
    residual = pd.to_numeric(early["postoperative_residual"], errors="coerce")
    events = followup["mri_status"].eq("confirmed_progression")
    surgery_dates = _date(baseline["index_surgery_date"])
    followup_dates = _date(followup["assessment_date"])
    followup_years = (followup_dates - surgery_dates).dt.days / 365.25

    lines = [
        "# 研究 01 描述性队列与路径报告",
        "",
        "> 仅描述数据中的记录和路径；不比较疗效、不作因果推断、不构成临床建议。",
        "",
        "## 队列概况",
        "",
        f"- 患者数：{len(patient_ids)}",
        f"- 手术年龄中位数：{ages.median():.1f} 岁" if ages.notna().any() else "- 手术年龄中位数：NA",
        f"- 术前肿瘤体积中位数：{volumes.median():.2f} mL" if volumes.notna().any() else "- 术前肿瘤体积中位数：NA",
        f"- Knosp 分级中位数：{knosp.median():.1f}" if knosp.notna().any() else "- Knosp 分级中位数：NA",
        f"- 首次术后可见残留：{int(residual.eq(1).sum())}/{len(early)}",
        f"- 记录为确认影像进展：{int(events.sum())}/{len(followup)}",
        f"- 随访时长中位数：{followup_years.median():.2f} 年" if followup_years.notna().any() else "- 随访时长中位数：NA",
        "",
        "## 实际治疗路径",
        "",
        "| 路径 | 患者数 |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {path} | {count} |" for path, count in path_counts.items())

    lines.extend([
        "",
        "## 事件日期完整性",
        "",
        f"- 含药物开始日期的记录：{int(medication['start_date'].notna().sum())}/{len(medication)}",
        f"- 含实际放疗日期的记录：{int(radiotherapy['rt_actual_date'].notna().sum())}/{len(radiotherapy)}",
        f"- 含再次手术日期的记录：{int(reoperation['reoperation_date'].notna().sum())}/{len(reoperation)}",
        f"- 含随访评估日期的记录：{int(followup['assessment_date'].notna().sum())}/{len(followup)}",
        "",
        "## 使用限制",
        "",
        "- 路径反映实际记录，不代表预先分配的治疗策略。",
        "- 不同路径患者的残留体积、生化活动和可手术性可能不同，不能由本报告比较疗效。",
        "- 进入策略比较前，必须完成数据质量、结局裁决和混杂因素审计。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(build_summary(args.data_dir), encoding="utf-8")
    print(f"Wrote descriptive report: {args.output}")


if __name__ == "__main__":
    main()
