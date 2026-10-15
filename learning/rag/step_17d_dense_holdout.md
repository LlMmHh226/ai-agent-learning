# 17d · Dense 留出题

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

固定阈值后才观察新题分数。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17c_02 留出验证](step_17c_02_holdout_eval.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_17d_dense_holdout.py)：学习代码，关键定义：`DenseHoldoutMetrics`, `evaluate_fixed_threshold`, `main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
文档批量编码+留出题批量编码
→ 排序
→ 固定阈值统计
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def evaluate_fixed_threshold(
    observations: list[DenseScoreObservation],
    threshold: float,
) -> DenseHoldoutMetrics:
    if not observations:
        raise ValueError("留出评测观察值不能为空")

    positive_correct = 0
    positive_rejected = 0
    positive_wrong_source = 0
    negative_rejected = 0
    negative_passed = 0

    for observation in observations:
        passed = observation.top_score >= threshold

        if observation.expected_source is None:
            if passed:
                negative_passed += 1
            else:
                negative_rejected += 1
        elif not passed:
            positive_rejected += 1
        elif observation.top_source == observation.expected_source:
            positive_correct += 1
        else:
            positive_wrong_source += 1

```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_17d_dense_holdout
```


**应观察到：** 输出正例误拒、错排、负例误放；不测聊天幻觉率。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 相关文档可能没有回答所需事实，来源正确不等于证据充分。

## 自测与参考答案

1. 为什么 Top-1 来源正确仍可能误放负例？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 相关文档可能没有回答所需事实，来源正确不等于证据充分。
2. 文档批量编码+留出题批量编码 → 排序 → 固定阈值统计。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“固定阈值后才观察新题分数”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
