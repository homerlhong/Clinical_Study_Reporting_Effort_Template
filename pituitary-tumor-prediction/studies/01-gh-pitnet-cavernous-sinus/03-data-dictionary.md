# 研究 01 数据字典：GH 瘤、海绵窦侵袭与多模式治疗

## 使用原则

- 一行 `patient_id` 对应一名去标识化患者；重复事件（MRI、激素、用药、SRS/GK、手术）使用独立事件表，以日期连接。
- 所有日期均使用相对研究时间或受控日期环境保存；公开仓库不保存真实患者记录。
- 缺失值使用 `NA`，并用 `missing_reason` 记录原因；不得用 0、空字符串或“未见异常”代替缺失。
- 变量在进入模型前必须标识：是否在对应预测时间点可得。

## 表 1：患者与诊断基线（`patient_baseline`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `patient_id` | 字符 | 全程 | 去标识化唯一 ID |
| `index_surgery_date` | 日期 | 零时点 | 首次经蝶手术日期 |
| `age_at_surgery_years` | 数值/年 | 零时点 | 手术时年龄 |
| `sex_at_birth` | 分类 | 基线 | 数据源原始定义 |
| `acromegaly_diagnosis_basis` | 分类 | 诊断 | 临床/IGF-1/GH/OGTT/MRI 的组合证据 |
| `symptom_onset_date_or_interval` | 日期或间隔 | 诊断前 | 可不精确，但记录精度 |
| `tumor_subtype` | 分类 | 诊断/病理 | GH 单分泌、GH/PRL 混合等 |
| `familial_or_genetic_flag` | 0/1/不明 | 基线 | 遗传性或家族史线索 |
| `prior_pitnet_treatment` | 0/1 | 基线 | 若为 1，主队列通常排除 |

## 表 2：术前临床与内分泌（`preop_endocrine`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `sample_date` | 日期 | 每次检测 | 采样日期 |
| `hormone_name` | 分类 | 每次检测 | IGF-1、随机 GH、OGTT GH nadir、PRL 等 |
| `hormone_value` | 数值 | 每次检测 | 原始数值，不先行转换 |
| `hormone_unit` | 分类 | 每次检测 | 必填 |
| `reference_lower` / `reference_upper` | 数值 | 每次检测 | 同期参考区间 |
| `assay_platform` | 分类 | 每次检测 | 实验室/平台/方法（如可得） |
| `medication_state_at_sampling` | 分类 | 每次检测 | 未用药/药物名/剂量背景 |
| `igf1_uln_ratio` | 数值 | 派生 | IGF-1 ÷ 同期年龄性别校正 ULN |
| `visual_field_deficit` | 0/1/不明 | 术前 | 需有检查日期和方法 |
| `visual_acuity_deficit` | 0/1/不明 | 术前 | 需有检查日期和方法 |
| `pituitary_axis_deficits` | 分类 | 术前 | 各轴分开存储，不用单一总分替代 |
| `acromegaly_comorbidities` | 多标签 | 术前 | 高血压、糖代谢、OSA、心血管等；用于风险调整 |

## 表 3：术前 MRI 与海绵窦侵袭（`preop_mri`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `mri_date` | 日期 | 术前 | 与手术间隔天数可派生 |
| `scanner_vendor` / `field_strength_t` | 分类/数值 | MRI | 控制设备差异 |
| `sequence_protocol` | 分类 | MRI | 至少记录增强 T1 等关键序列 |
| `max_diameter_mm` | 数值/mm | MRI | 明确测量轴 |
| `tumor_volume_ml` | 数值/mL | MRI | 优先保存分割方法与版本 |
| `knosp_grade` | 整数/不明 | MRI | 原始分级 + 阅片来源 |
| `radiologic_cavernous_sinus_invasion` | 0/1/不明 | MRI | 预设影像定义 |
| `invasion_confidence` | 分类 | MRI | 明确/可能/不确定 |
| `suprasellar_extension` | 0/1 | MRI | 结构化评估 |
| `optic_chiasm_compression` | 0/1 | MRI | 结构化评估 |
| `ica_encasement_or_contact` | 分类 | MRI | 无/接触/部分包绕/其他 |
| `image_reviewer_id` / `review_type` | 字符/分类 | MRI | 原报告/中央复核/双人复核 |

## 表 4：首次手术与病理（`index_surgery_pathology`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `surgery_date` | 日期 | 零时点 | 应等于 index_surgery_date |
| `surgical_approach` | 分类 | 手术 | 经蝶内镜/显微或其他 |
| `operative_cavernous_sinus_involvement` | 0/1/不明 | 手术 | 术中记录，不替代 MRI |
| `extent_of_resection` | 分类 | 手术后 | 总切除/次全/部分/不确定 |
| `residual_reason` | 多标签 | 手术后 | 海绵窦、颈内动脉、视路、肿瘤质地等 |
| `intraoperative_complications` | 多标签 | 手术 | 结构化编码 |
| `cell_lineage` | 分类 | 病理 | PIT1、TPIT、SF1、混合/不定 |
| `hormone_ihc_profile` | 多标签 | 病理 | 保存原始染色结果 |
| `granulation_pattern` | 分类 | 病理 | 稠密/稀疏/不明（如可得） |
| `ki67_percent` | 数值/% | 病理 | 保存原始百分比和计数方式 |
| `mitotic_count` | 数值 | 病理 | 同时保存单位/视野定义 |
| `p53_ihc` | 分类 | 病理 | 平台、评分规则可追溯 |
| `pathology_review_status` | 分类 | 病理 | 原始/中央复核/一致性待定 |

## 表 5：术后早期状态（`early_postop`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `postop_mri_date` | 日期 | 首次术后 MRI | 记录距手术天数 |
| `postoperative_residual` | 0/1/不明 | 首次术后 MRI | 仅指可见残留 |
| `residual_volume_ml` | 数值/mL | 首次术后 MRI | 原始测量与方法 |
| `residual_max_diameter_mm` | 数值/mm | 首次术后 MRI | 无残留为 0；不确定为 NA |
| `residual_location` | 多标签 | 首次术后 MRI | 海绵窦/鞍上/鞍内/其他 |
| `early_igf1_date` / `early_igf1_uln_ratio` | 日期/数值 | 预设窗口 | 不同时间窗口不得静默合并 |
| `early_gh_date` / `early_gh_value` | 日期/数值 | 预设窗口 | 单位和检测平台必填 |
| `early_biochemical_status` | 分类 | 预设窗口 | 控制/持续活动/不确定 |
| `new_postop_axis_deficit` | 多标签 | 术后 | 各轴独立记录 |
| `postop_visual_status` | 分类 | 术后 | 改善/稳定/恶化/不明 |

## 表 6：药物暴露（`medication_events`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `medication_name` | 分类 | 每次事件 | SSA、培维索孟、卡麦角林等按实际名称 |
| `start_date` / `stop_date` | 日期 | 暴露期 | 未停用则右删失 |
| `dose` / `dose_unit` / `frequency` | 数值/分类 | 暴露期 | 保留每次调整 |
| `treatment_intent` | 分类 | 开始时 | 术后控制、桥接、进展后等 |
| `reason_for_change` | 多标签 | 调整时 | 无效、不耐受、偏好、可及性等 |
| `adherence_assessment` | 分类 | 随访 | 有证据/不明；不可假设 |

## 表 7：SRS/GK 与其他放疗（`radiotherapy_events`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `rt_actual_date` | 日期 | 实际照射 | 暴露日期；非计划日期 |
| `rt_modality` | 分类 | 放疗 | GK、LINAC SRS、分割 SRT、常规 RT 等 |
| `rt_indication` | 多标签 | 决策时 | 残留、持续生化活动、进展、不可再手术等 |
| `target_volume_ml` | 数值/mL | 计划时 | 靶区体积 |
| `margin_dose_gy` | 数值/Gy | 计划时 | 单次或分割需说明 |
| `fraction_count` | 整数 | 计划时 | 分割数 |
| `optic_pathway_max_dose_gy` | 数值/Gy | 计划时 | 安全性关键变量 |
| `pituitary_stalk_or_normal_gland_dose` | 数值/Gy/不明 | 计划时 | 如可得 |
| `distance_to_optic_apparatus_mm` | 数值/mm | 计划时 | 与计划评估日期对应 |
| `concurrent_medication_state` | 分类 | 照射时 | 影响生化反应解释 |

## 表 8：再次手术（`reoperation_events`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `reoperation_date` | 日期 | 事件 | 实际手术日 |
| `reoperation_indication` | 多标签 | 决策时 | 压迫、可达残留、进展、生化活动等 |
| `pre_reoperation_mri_date` | 日期 | 事件前 | 与手术对应的影像依据 |
| `pre_reoperation_biochemical_status` | 分类 | 事件前 | 控制/持续活动/不确定 |
| `reoperation_outcome` | 分类 | 术后 | 按单独随访表验证 |

## 表 9：纵向随访与结局（`followup_events`）

| 字段 | 类型/单位 | 时间点 | 说明 |
| --- | --- | --- | --- |
| `assessment_date` | 日期 | 每次随访 | 统一事件时间轴 |
| `mri_status` | 分类 | 每次 MRI | 无残留/稳定残留/缩小/疑似进展/确认进展 |
| `tumor_volume_ml` | 数值/mL | 每次 MRI | 同一分割策略优先 |
| `igf1_uln_ratio` | 数值 | 每次激素 | 与检测日期及用药状态关联 |
| `gh_value` / `gh_unit` | 数值/分类 | 每次激素 | 保留原始数据 |
| `biochemical_control_status` | 分类 | 每次评估 | 按预先定义 |
| `new_hypopituitarism` | 多标签 | 每次评估 | 轴、起始日期、替代治疗 |
| `visual_or_cranial_nerve_event` | 多标签 | 每次评估 | 事件日期与评估方法 |
| `patient_reported_outcome` | 数值/分类 | 每次评估 | 量表名、版本、分数 |
| `event_adjudication_status` | 分类 | 候选事件 | 已确认/未确认/信息不足 |
| `last_known_event_free_date` | 日期 | 末次随访 | 用于删失 |
| `lost_to_followup_reason` | 分类 | 失访时 | 关键偏倚变量 |

## 核心派生变量（不可覆盖原始数据）

- `days_from_index_surgery`：所有事件与零时点的间隔。
- `time_to_first_rt_days`：首次实际照射前的时间。
- `time_to_reoperation_days`：再次手术前的时间。
- `best_igf1_uln_ratio_by_window`：在预设窗口内计算，保留窗口定义。
- `progression_or_retreatment_3y`：按结局框架裁决。
- `new_hypopituitarism_after_rt`：仅在照射前无对应轴缺乏且之后新发时计入。

## 最小质控规则

1. `rt_actual_date` 不能早于 `index_surgery_date`。
2. 首次术后 MRI 日期必须晚于手术日期。
3. 激素值没有单位、日期或检测名称时，不进入建模。
4. 进展事件必须能连接至少一个证据来源和裁决状态。
5. 任何派生标签必须能追溯到原始字段与生成脚本。

## 下一步

用这份字典建立空白数据模板和数据质量检查规则；模板只包含字段，不包含真实患者数据。
