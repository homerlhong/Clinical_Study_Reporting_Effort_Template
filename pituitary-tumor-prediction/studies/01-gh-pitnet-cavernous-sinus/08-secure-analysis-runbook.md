# 研究 01 安全分析运行手册

## 目的

本手册将研究 01 的文档、模板和代码串成一个可复现流程。真实患者数据只能在经批准的受控环境中运行；不得复制到公开 GitHub、本地个人目录或聊天内容。

## 运行前提

- 已完成 `07-data-source-mapping.md` 的字段级映射。
- 已完成研究伦理、数据使用授权和访问控制。
- 已将真实 CSV 放在受控的 `DATA_DIR` 中；该目录不在 Git 仓库内。
- 已冻结本次运行的数据截点、映射版本和代码提交哈希。

## 目录约定

```text
DATA_DIR/                     # 受控真实数据，不提交 Git
  patient_baseline.csv
  preop_endocrine.csv
  ...
OUTPUT_DIR/                   # 受控聚合结果
```

## 第 1 步：结构与时间顺序质控

```bash
python -m src.validate_research01 --data-dir "$DATA_DIR"
```

**通过条件：** 所有必需表、字段、患者 ID 与基础时间顺序检查通过。

**失败时：** 停止；回到数据映射和清洗，不删除“麻烦病例”来让质控通过。

## 第 2 步：生成数据可用性报告

```bash
python -m src.report_research01_data_quality \
  --data-dir "$DATA_DIR" \
  --output "$OUTPUT_DIR/data_quality_report.md"
```

审核：关键 MRI、早期 IGF-1/GH、放疗参数、结局裁决和随访字段的覆盖；比较不同治疗路径的缺失是否系统性不同。

## 第 3 步：运行准备度闸门

使用 `06-study-readiness-gate.md` 完成 A–E 五项审核并存档。

**通过条件：** 队列、时间轴、结局和关键混杂因素足以支持所计划的分析。

**失败时：** 可继续描述性分析，但不进行预测模型或策略比较。

## 第 4 步：描述队列与真实路径

```bash
python -m src.analyze_research01_descriptive \
  --data-dir "$DATA_DIR" \
  --output "$OUTPUT_DIR/descriptive_path_report.md"
```

审核：患者数量、事件数、术后残留、药物/SRS/GK/再次手术时间线和失访。

## 第 5 步：建立 landmark 队列

```bash
python -m src.build_research01_landmark_cohort \
  --data-dir "$DATA_DIR" \
  --output "$OUTPUT_DIR/landmark_cohort.csv" \
  --grace-days 180
```

输出中的策略标签仅用于研究比较；必须核对 landmark 日期、宽限期和未赋值患者原因。

## 第 6 步：诊断策略可比性

```bash
python -m src.report_research01_strategy_balance \
  --cohort "$OUTPUT_DIR/landmark_cohort.csv" \
  --output "$OUTPUT_DIR/strategy_balance.md"
```

**通过条件：** 两策略均有足够样本与事件，关键混杂因素可测量；若样本过小或 SMD 不可估，停止策略效应分析。

## 第 7 步：运行研究型基线预测模型

```bash
python -m src.train_research01_baseline_model \
  --data-dir "$DATA_DIR" \
  --output "$OUTPUT_DIR/baseline_model_report.json"
```

报告应包括：符合 3 年结局资格的人数、事件数、交叉验证方式、AUC、Brier 分数和校准评估。该输出仅是内部研究结果，不能直接用于临床。

## 每次运行必须存档

- 数据截点和数据映射版本；
- 代码提交哈希与 Python / 依赖版本；
- 分析参数：landmark 规则、宽限期、结局版本；
- 质控报告、准备度审核、路径报告、平衡报告和模型报告；
- 任何人工裁决、例外处理和敏感性分析的日志。

## 禁止事项

- 不把患者级 CSV、影像、遗传结果或可识别报告上传至 GitHub。
- 不在未通过准备度闸门时训练模型或宣布疗效结果。
- 不将内部交叉验证性能写成临床有效性或对个体患者提供治疗建议。
- 不在没有临床与统计审核的情况下，把观察性比较解释为因果结论。

## 当前项目状态

代码流程已在模拟数据上运行。真实数据运行必须在合规批准后由授权人员在受控环境中完成。
