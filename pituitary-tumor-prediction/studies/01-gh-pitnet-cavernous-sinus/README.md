# 研究 01｜海绵窦侵袭生长激素瘤的多模式治疗路径

## 项目目的

研究首次经蝶手术后、合并海绵窦侵袭的 GH 分泌 PitNET / 肢端肥大症患者，如何描述并评估“药物治疗、早期/延迟 SRS 或伽马刀、再次手术”等真实治疗路径与长期肿瘤控制、内分泌控制和功能安全性的关系。

这是一个研究与方法学项目，不提供个体患者治疗建议。

## 研究逻辑

```text
明确队列与结局
→ 统一多源变量和时间轴
→ 描述真实世界路径
→ 建立可解释风险预测
→ 在可比人群中谨慎比较治疗策略
→ 在时间外或外部数据中验证
```

## 文档导航

| 阶段 | 文档 | 作用 |
| --- | --- | --- |
| 队列 | [01-cohort-definition.md](01-cohort-definition.md) | 定义成人 GH 瘤、海绵窦侵袭与研究零时点 |
| 路径 | [02-treatment-pathways.md](02-treatment-pathways.md) | 定义药物、早期/延迟 SRS/GK 与再次手术路径 |
| 变量 | [03-data-dictionary.md](03-data-dictionary.md) | 九张研究表、时间戳与质控字段 |
| 分析 | [04-statistical-analysis-plan.md](04-statistical-analysis-plan.md) | 描述、预测与策略比较的统计方案 |
| 目标试验 | [05-target-trial-early-srs-vs-medical.md](05-target-trial-early-srs-vs-medical.md) | 早期 SRS/GK 与药物优先的可审计比较框架 |
| 准备度 | [06-study-readiness-gate.md](06-study-readiness-gate.md) | 进入真实建模前的五道闸门 |
| 数据映射 | [07-data-source-mapping.md](07-data-source-mapping.md) | 从病历、LIS、PACS、病理和放疗系统映射变量 |
| 运行 | [08-secure-analysis-runbook.md](08-secure-analysis-runbook.md) | 受控环境中的端到端执行流程 |

## 代码导航

| 工具 | 路径 | 用途 |
| --- | --- | --- |
| 质控 | [`src/validate_research01.py`](../../src/validate_research01.py) | 检查表结构、必填字段与基础时间顺序 |
| 数据可用性 | [`src/report_research01_data_quality.py`](../../src/report_research01_data_quality.py) | 汇总覆盖、缺失、日期跨度和关键变量可用率 |
| 路径描述 | [`src/analyze_research01_descriptive.py`](../../src/analyze_research01_descriptive.py) | 描述队列与实际治疗序列，不比较疗效 |
| landmark 队列 | [`src/build_research01_landmark_cohort.py`](../../src/build_research01_landmark_cohort.py) | 构建早期 SRS/GK 与药物优先的策略标签 |
| 平衡诊断 | [`src/report_research01_strategy_balance.py`](../../src/report_research01_strategy_balance.py) | 检查策略组在调整前的协变量差异 |
| 基线预测 | [`src/train_research01_baseline_model.py`](../../src/train_research01_baseline_model.py) | 研究型 3 年风险模型原型 |
| 模拟数据 | [`src/generate_research01_synthetic_data.py`](../../src/generate_research01_synthetic_data.py) | 仅用于测试流程的虚构多表数据 |

## 当前完成状态

- [x] 明确研究人群、结局和治疗路径。
- [x] 完成专属数据字典和空白多表模板。
- [x] 完成结构/时间质控、可用性报告、描述性路径报告。
- [x] 完成 landmark 队列、策略平衡诊断和研究型基线模型原型。
- [x] 用模拟数据完成端到端测试。
- [ ] 在受控环境中完成真实数据映射与质量审核。
- [ ] 完成真实队列的结局裁决与准备度闸门审核。
- [ ] 执行真实预测模型和策略比较。
- [ ] 完成时间外/外部验证和临床影响评估。

## 数据与安全边界

真实患者数据、原始影像、病理切片、基因/组学结果和可识别随访信息不得上传到此公开仓库。公开内容仅包括方案、空白模板、代码、模拟数据生成器和经批准的聚合结果。

## 下一件事

当获得合规数据访问后，从字段映射表开始，生成首份数据可用性报告；在准备度闸门通过前，不运行真实患者层面的预测或策略效应分析。
