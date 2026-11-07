# 数据字典（第一版）

| 变量 | 类型 | 预测时间点 | 定义 |
| --- | --- | --- | --- |
| `age_years` | 数值 | 首次手术 | 手术时年龄 |
| `max_diameter_mm` | 数值 | 术前 MRI | 最大径，毫米 |
| `cavernous_sinus_invasion` | 0/1 | 术前 MRI | 按预设影像标准记录 |
| `functional_tumor` | 0/1 | 诊断 | 是否存在明确激素高分泌综合征 |
| `postoperative_residual` | 0/1 | 术后首次 MRI | 是否存在残留肿瘤 |
| `early_biochemical_response` | 0/1 | 预设早期窗口 | 是否达到预设激素/生化反应标准 |
| `progression_or_retreatment_3y` | 0/1 | 3 年随访 | 主要复合结局 |

真实队列应补充：测量日期、来源、缺失原因、检测方法与单位、结局裁决者和不确定性标记。
