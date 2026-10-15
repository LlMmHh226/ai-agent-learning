# 16h_02 · 检索器对比

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

在同题同 K 下比较。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/16h_01 评测集与基线](step_16h_01_eval_dataset_and_ngram_baseline.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_16h_02_compare_retrievers.py)：学习代码，关键定义：`RetrieverComparison`, `PrecomputedEmbeddingService`, `main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
同一问题集
→ n-gram/Dense/Hybrid
→ 召回、精度、耗时
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    chunks = split_documents(
        documents=load_markdown_documents(),
        chunk_size=10_000,
        overlap=0,
    )
    questions = [case.question for case in EVALUATION_CASES]
    embedding_service = EmbeddingService()

    try:
        document_start = perf_counter()
        document_vectors = embedding_service.embed_documents(
            [chunk.content for chunk in chunks]
        )
        document_batch_ms = (perf_counter() - document_start) * 1000

        query_start = perf_counter()
        query_vectors = embedding_service.embed_queries(questions)
        query_batch_ms = (perf_counter() - query_start) * 1000
    except EmbeddingServiceError as error:
        print(f"真实 Embedding 评测停止：{error}")
        raise SystemExit(1) from error

    precomputed_service = PrecomputedEmbeddingService(
        document_vectors_by_text={
            chunk.content: vector
            for chunk, vector in zip(chunks, document_vectors)
        },
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_16h_02_compare_retrievers
```


**应观察到：** 文档与问题分别批量编码后复用向量，避免每个 K 重复请求。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 不能；应分别说明编码、缓存与排序时间，避免漏算外部请求。

## 自测与参考答案

1. 向量预计算后耗时能代表完整在线延迟吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；应分别说明编码、缓存与排序时间，避免漏算外部请求。
2. 同一问题集 → n-gram/Dense/Hybrid → 召回、精度、耗时。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“在同题同 K 下比较”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
