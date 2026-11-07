# 第一版最小变量集（MVP）

## 预测任务

**预测时间点：** 首次手术后，完成首次术后 MRI 和预设早期激素评估时。

**目标：** 估计患者在术后 3 年内发生影像学进展或因肿瘤控制不足而接受再治疗的风险。

**重要：** 表中的所有预测变量必须在预测时间点或之前可获得。不得使用预测时点之后的信息。

## 20 个预测变量

| # | 变量名 | 类型 | 时间点 | 收集规则 |
| --- | --- | --- | --- | --- |
| 1 | age_years | 数值 | 首次手术日 | 手术时年龄（岁） |
| 2 | sex_at_birth | 分类 | 基线 | 记录为数据源定义的值 |
| 3 | tumor_subtype | 分类 | 诊断/病理 | 功能性亚型或非功能性；保留原始病理文本 |
| 4 | cell_lineage | 分类 | 病理 | PIT1、TPIT、SF1、未定或缺失 |
| 5 | max_diameter_mm_preop | 数值 | 术前 MRI | 明确 MRI 日期与测量轴 |
| 6 | tumor_volume_ml_preop | 数值 | 术前 MRI | 可得时记录；不可得则标记缺失，不以直径替代 |
| 7 | cavernous_sinus_invasion | 0/1 | 术前 MRI | 采用预先约定的影像判定标准 |
| 8 | suprasellar_extension | 0/1 | 术前 MRI | 按结构化报告或影像复核记录 |
| 9 | optic_pathway_compression | 0/1 | 术前 MRI | 记录视交叉/视路受压 |
| 10 | baseline_hormone_value | 数值 | 治疗前 | 与 hormone_name、单位和检测日期成组保存 |
| 11 | hormone_name | 分类 | 治疗前 | 如 PRL、IGF-1、ACTH/皮质醇；不同亚型不得静默混合 |
| 12 | visual_or_neurologic_deficit | 0/1 | 治疗前 | 以预设临床定义记录 |
| 13 | prior_tumor_treatment | 0/1 | 手术前 | 是否接受过相关手术、放疗或系统治疗 |
| 14 | surgical_approach | 分类 | 首次手术 | 例如经蝶/其他；记录实际术式 |
| 15 | postoperative_residual | 0/1 | 首次术后 MRI | 有无可见残留；记录 MRI 日期 |
| 16 | residual_max_diameter_mm | 数值 | 首次术后 MRI | 无残留时记录 0；不确定时缺失并说明原因 |
| 17 | residual_location | 分类 | 首次术后 MRI | 海绵窦、鞍上、鞍内、其他/多部位 |
| 18 | early_biochemical_response | 0/1 | 预设早期窗口 | 按亚型预先规定的激素目标评估 |
| 19 | ki67_percent | 数值 | 病理 | 原始百分比；同时记录检测实验室/方法（如可得） |
| 20 | proliferation_or_high_risk_pathology_flag | 0/1 | 病理 | 只按预先定义的组合规则生成，保留组成部分 |

## 主要结局（不作为预测变量）

`progression_or_retreatment_3y`：从首次手术日起 3 年内，发生以下任一事件：

1. 经预先定义、可追溯的影像学进展；或
2. 因肿瘤控制不足实施再手术、放疗或新增系统性肿瘤治疗。

必须另行记录：

- `event_date`
- `event_type`
- `event_evidence`（影像、病历或治疗记录）
- `last_followup_date`
- `lost_to_followup_reason`

## 暂不进入第一版的变量

- 预测时点以后的 MRI、激素、用药或再治疗信息。
- 未结构化且无法复核的自由文本特征。
- 未完成质控的组学数据。
- 样本极少且缺失严重的候选标志物。

## 数据收集的三个硬规则

1. **每个值必须有日期。** 没有日期，就无法判断它是否发生在预测时点之前。
2. **每个激素值必须有名称、单位和检测方法线索。** 不同指标或单位不能直接混合。
3. **缺失不是零。** 记录缺失原因；不在原始数据阶段擅自填补。
