"""Create a non-clinical data-availability report for research-01 CSV tables."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.validate_research01 import REQUIRED_COLUMNS, validate


DATE_COLUMNS = {
    "patient_baseline.csv": "index_surgery_date",
    "preop_endocrine.csv": "sample_date",
    "preop_mri.csv": "mri_date",
    "index_surgery_pathology.csv": "surgery_date",
    "early_postop.csv": "postop_mri_date",
    "medication_events.csv": "start_date",
    "radiotherapy_events.csv": "rt_actual_date",
    "reoperation_events.csv": "reoperation_date",
    "followup_events.csv": "assessment_date",
}


def _read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype="string", keep_default_na=False).replace("", pd.NA)


def _percent(numerator: int, denominator: int) -> str:
    return "NA" if denominator == 0 else f"{100 * numerator / denominator:.1f}%"


def build_report(data_dir: Path) -> str:
    """Return Markdown that summarizes structural availability, not clinical validity."""
    qc_errors = validate(data_dir)
    lines = [
        "# 研究 01 数据可用性报告",
        "",
        f"生成时间（UTC）：{datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "> 此报告只检查数据覆盖、缺失和时间范围；不评估临床正确性，也不产生任何患者层面的结论。",
        "",
        "## 结构质控",
        "",
    ]
    if qc_errors:
        lines.extend(["**未通过。**", ""] + [f"- {error}" for error in qc_errors])
    else:
        lines.extend(["**通过。** 所有必需表、字段和基础时间顺序检查均通过。", ""])

    lines.extend([
        "## 表覆盖与缺失",
        "",
        "| 表 | 记录数 | 唯一患者数 | 关键日期范围 | 必填列缺失 |",
        "| --- | ---: | ---: | --- | ---: |",
    ])
    for filename, required_columns in REQUIRED_COLUMNS.items():
        path = data_dir / filename
        if not path.exists():
            lines.append(f"| `{filename}` | 缺失 | — | — | — |")
            continue
        table = _read_table(path)
        patient_count = table["patient_id"].nunique(dropna=True) if "patient_id" in table else 0
        date_column = DATE_COLUMNS[filename]
        parsed_dates = pd.to_datetime(table[date_column], errors="coerce") if date_column in table else pd.Series(dtype="datetime64[ns]")
        valid_dates = parsed_dates.dropna()
        date_range = "NA" if valid_dates.empty else f"{valid_dates.min().date()} 至 {valid_dates.max().date()}"
        missing_required = sum(int(table[column].isna().sum()) for column in required_columns if column in table)
        lines.append(f"| `{filename}` | {len(table)} | {patient_count} | {date_range} | {missing_required} |")

    lines.extend(["", "## 关键字段可用性", ""])
    key_fields = {
        "preop_mri.csv": ["knosp_grade", "radiologic_cavernous_sinus_invasion", "tumor_volume_ml"],
        "early_postop.csv": ["postoperative_residual", "residual_volume_ml", "early_igf1_uln_ratio"],
        "radiotherapy_events.csv": ["rt_modality", "target_volume_ml", "margin_dose_gy", "optic_pathway_max_dose_gy"],
        "followup_events.csv": ["mri_status", "igf1_uln_ratio", "biochemical_control_status", "event_adjudication_status"],
    }
    lines.extend(["| 表 / 字段 | 非缺失数 | 可用率 |", "| --- | ---: | ---: |"])
    for filename, fields in key_fields.items():
        path = data_dir / filename
        if not path.exists():
            continue
        table = _read_table(path)
        for field in fields:
            available = int(table[field].notna().sum()) if field in table else 0
            lines.append(f"| `{filename}` / `{field}` | {available} | {_percent(available, len(table))} |")

    lines.extend([
        "",
        "## 自动判读提示",
        "",
        "- 若结构质控未通过，先修正字段与日期问题，暂不建模。",
        "- 若早期 MRI、早期 IGF-1 或放疗关键剂量字段缺失严重，应调整研究问题或开展数据补全，而不是静默删除患者。",
        "- 该报告不替代影像、病理、内分泌或事件裁决复核。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(build_report(args.data_dir), encoding="utf-8")
    print(f"Wrote data availability report: {args.output}")


if __name__ == "__main__":
    main()
