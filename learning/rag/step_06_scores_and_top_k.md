# 06 · 分数与 Top-K

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

观察排序和阈值的不同职责。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/05 字符 n-gram 检索](step_05_ngram_retriever.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_06_show_all_scores.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
问题
→ 所有 chunk 分数
→ min_score 过滤
→ Top-K
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    RetrievalResult,
    build_char_ngrams,
    calculate_ngram_similarity,
    retrieve,
)


query = "物流轨迹超过 48 小时没有更新怎么办？"
top_k = 2

documents = load_markdown_documents()
chunks = split_documents(documents)
query_ngrams = build_char_ngrams(query)
all_results: list[RetrievalResult] = []

for chunk in chunks:
    score = calculate_ngram_similarity(
        query=query,
        chunk_text=chunk.content,
    )
    all_results.append(
        RetrievalResult(
            document=chunk,
            score=score,
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_06_show_all_scores
```


**应观察到：** 输出所有分数与最终候选，改变 K 可观察候选数。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不保证；语料数量与阈值过滤可能使结果少于 K。

## 自测与参考答案

1. Top-K=3 是否保证返回三条？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不保证；语料数量与阈值过滤可能使结果少于 K。
2. 问题 → 所有 chunk 分数 → min_score 过滤 → Top-K。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“观察排序和阈值的不同职责”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
