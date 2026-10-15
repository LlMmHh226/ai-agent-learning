# 16i_01 · 向量库决策

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

按规模与需求选择存储。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/16h_02 检索器对比](step_16h_02_compare_retrievers.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/rag/dense_retriever.py)：正式模块，关键定义：`DenseRetrievalResult`, `calculate_cosine_similarity`, `DenseRetriever`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
三篇知识文档
→ 当前内存排序成本
→ 比较持久化/过滤需求
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    def retrieve(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 3,
    ) -> list[DenseRetrievalResult]:
        if not query.strip():
            raise ValueError("query 不能为空字符串")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if not documents:
            return []

        embedded_documents = self.embedding_cache.get_embeddings(documents)
        query_vector = self.embedding_service.embed_query(query)

        results = [
            DenseRetrievalResult(
                document=embedded_document.document,
                score=calculate_cosine_similarity(
                    vector_a=query_vector,
                    vector_b=embedded_document.vector,
                ),
            )
            for embedded_document in embedded_documents
        ]
        results.sort(
            key=lambda result: result.score,
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_dense_retriever -v
```


**应观察到：** 此例暂不引入向量数据库，能说清升级条件。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 大量向量、持续更新、持久化、并发检索或 metadata 过滤等需求出现时。

## 自测与参考答案

1. 什么情况下需要考虑向量库？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 大量向量、持续更新、持久化、并发检索或 metadata 过滤等需求出现时。
2. 三篇知识文档 → 当前内存排序成本 → 比较持久化/过滤需求。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“按规模与需求选择存储”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
