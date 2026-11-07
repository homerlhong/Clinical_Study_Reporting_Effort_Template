# 研究 01 空白数据模板

这些 CSV 仅定义字段，不包含真实患者数据。真实数据不得提交到公开 GitHub；应在获得批准的安全环境中，将同结构模板用于受控数据。

## 使用方式

1. 以 `patient_id` 作为去标识化连接键。
2. 每个事件表可以为同一患者保留多行，且每行必须有相应日期。
3. 缺失填写 `NA`，并在适用时填写 `missing_reason`。
4. 导入前运行：`python -m src.validate_research01 --data-dir PATH_TO_CSVS`。

模板字段的权威说明见上级目录的 `03-data-dictionary.md`。
