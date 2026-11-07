"""Report pre-adjustment covariate balance for research-01 strategy labels.

The report is diagnostic only. It does not estimate treatment effects.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


COVARIATES = [
    "age_at_surgery_years",
    "tumor_volume_ml",
    "knosp_grade",
    "residual_volume_ml",
    "early_igf1_uln_ratio",
    "early_gh_value",
]


def _smd(first: pd.Series, second: pd.Series) -> float | None:
    first = pd.to_numeric(first, errors="coerce").dropna()
    second = pd.to_numeric(second, errors="coerce").dropna()
    if len(first) < 2 or len(second) < 2:
        return None
    pooled_sd = np.sqrt((first.var(ddof=1) + second.var(ddof=1)) / 2)
    return None if pooled_sd == 0 else float((first.mean() - second.mean()) / pooled_sd)


def build_report(cohort_path: Path) -> str:
    """Return a Markdown pre-adjustment comparison for assigned strategies."""
    cohort = pd.read_csv(cohort_path, dtype="string", keep_default_na=False).replace("", pd.NA)
    comparison = cohort[cohort["strategy_assignment"].isin(["early_SRS_GK", "medical_first"])].copy()
    early = comparison[comparison["strategy_assignment"] == "early_SRS_GK"]
    medical = comparison[comparison["strategy_assignment"] == "medical_first"]
    lines = [
        "# 研究 01 策略比较：赋值前协变量平衡报告",
        "",
        "> 此报告只呈现早期 SRS/GK 与药物优先策略组在 landmark 时的差异。它不估计疗效，不构成临床建议。",
        "",
        "## 样本量",
        "",
        f"- early_SRS_GK：{len(early)}",
        f"- medical_first：{len(medical)}",
        f"- 未赋值或不符合比较资格：{len(cohort) - len(comparison)}",
        "",
        "## 未调整协变量平衡",
        "",
        "| 变量 | early_SRS_GK 平均值 | medical_first 平均值 | 标准化均数差 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for covariate in COVARIATES:
        early_values = pd.to_numeric(early.get(covariate), errors="coerce")
        medical_values = pd.to_numeric(medical.get(covariate), errors="coerce")
        early_mean = "NA" if early_values.dropna().empty else f"{early_values.mean():.3f}"
        medical_mean = "NA" if medical_values.dropna().empty else f"{medical_values.mean():.3f}"
        smd = _smd(early_values, medical_values)
        smd_text = "NA" if smd is None else f"{smd:.3f}"
        lines.append(f"| `{covariate}` | {early_mean} | {medical_mean} | {smd_text} |")
    lines.extend([
        "",
        "## 解释规则",
        "",
        "- 标准化均数差（SMD）接近 0 表示该变量在两组间更接近；它不是显著性检验。",
        "- 常见经验阈值是绝对 SMD <0.1 作为较好平衡的提示，但不能替代临床判断。",
        "- 若任一组样本过小、方差为 0 或变量缺失，SMD 会显示 NA；此时不能据此开展可靠策略比较。",
        "- 此报告是加权、匹配或其他调整前的诊断。后续若使用因果方法，必须再次输出调整后的平衡报告。",
        "",
        "## 继续条件",
        "",
        "只有在两策略都有足够患者和事件、关键临床变量可测量、且存在合理的可交换性基础时，才考虑进入调整后的关联分析或目标试验模拟。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(build_report(args.cohort), encoding="utf-8")
    print(f"Wrote strategy balance report: {args.output}")


if __name__ == "__main__":
    main()
