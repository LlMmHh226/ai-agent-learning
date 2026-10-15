# 17c_01 · 阈值取舍

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

同时观察误放与误拒。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17b Dense 分数边界](step_17b_dense_score_eval.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_17c_01_threshold_tradeoff.py)：学习代码，关键定义：`ThresholdTradeoff`, `evaluate_threshold`, `main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
固定分数样例
→ 0.30/0.40/0.46
→ 分类计数
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def evaluate_threshold(
    observations: list[DenseScoreObservation],
    threshold: float,
) -> ThresholdTradeoff:
    if not observations:
        raise ValueError("评测观察值不能为空")

    positive_passed = 0
    positive_rejected = 0
    negative_passed = 0
    negative_rejected = 0

    for observation in observations:
        passed = observation.top_score >= threshold
        is_positive = observation.expected_source is not None

        if is_positive and passed:
            positive_passed += 1
        elif is_positive:
            positive_rejected += 1
        elif passed:
            negative_passed += 1
        else:
            negative_rejected += 1

    return ThresholdTradeoff(
        threshold=threshold,
        positive_passed=positive_passed,
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_17c_01_threshold_tradeoff
```


**应观察到：** 阈值升高可能减少误放，也增加正例误拒。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不说明；若大量可回答问题也被拒绝，系统可用性会下降。

## 自测与参考答案

1. 负例全拒绝就说明阈值最好吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不说明；若大量可回答问题也被拒绝，系统可用性会下降。
2. 固定分数样例 → 0.30/0.40/0.46 → 分类计数。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“同时观察误放与误拒”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
