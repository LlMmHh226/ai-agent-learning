# 16h_01 · 评测集与基线

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

先固定问题、标签和指标。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/16g RRF 混合召回](step_16g_hybrid_retriever.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_16h_01_ngram_eval_baseline.py)：学习代码，关键定义：`RetrievalEvalCase`, `RetrievalEvalMetrics`, `evaluate_retriever`, `main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
固定商品/物流/售后问题
→ n-gram
→ Recall/Precision
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def evaluate_retriever(
    cases: list[RetrievalEvalCase],
    retrieve_sources: Callable[[str, int], list[str]],
    k: int,
) -> RetrievalEvalMetrics:
    if not cases:
        raise ValueError("评测用例不能为空")
    if k <= 0:
        raise ValueError("k 必须大于 0")

    hit_count = 0
    returned_result_count = 0
    latencies_ms: list[float] = []

    for case in cases:
        start_time = perf_counter()
        returned_sources = retrieve_sources(case.question, k)
        elapsed_ms = (perf_counter() - start_time) * 1000
        latencies_ms.append(elapsed_ms)

        hit = case.expected_source in returned_sources
        if hit:
            hit_count += 1
        returned_result_count += len(returned_sources)

        print(
            f"K={k} 命中={hit!s:5} "
            f"预期={case.expected_source:14} "
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_16h_01_ngram_eval_baseline
```


**应观察到：** 得到可重复的本地基线，标签应人工核对。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 避免为某个方法选择有利样本，确保比较基于同一问题与标准。

## 自测与参考答案

1. 为什么比较前先固定评测题？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 避免为某个方法选择有利样本，确保比较基于同一问题与标准。
2. 固定商品/物流/售后问题 → n-gram → Recall/Precision。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“先固定问题、标签和指标”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
