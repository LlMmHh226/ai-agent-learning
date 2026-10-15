# 17b · Dense 分数边界

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

观察正负分数是否交叉。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17a 无答案负例](step_17a_no_answer_eval.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_17b_dense_score_eval.py)：学习代码，关键定义：`DenseScoreCase`, `DenseScoreObservation`, `DenseScoreBoundary`, `build_observations`, `analyze_score_boundary`, `main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
正例和无答案负例
→ 真 Embedding
→ Top-1 分数
→ 范围比较
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def build_observations(
    cases: list[DenseScoreCase],
    query_vectors: list[list[float]],
    documents: list[Document],
    document_vectors: list[list[float]],
) -> list[DenseScoreObservation]:
    if len(cases) != len(query_vectors):
        raise ValueError("问题数量与 query 向量数量不一致")
    if len(documents) != len(document_vectors):
        raise ValueError("文档数量与 document 向量数量不一致")
    if not documents:
        raise ValueError("候选文档不能为空")

    observations: list[DenseScoreObservation] = []
    for case, query_vector in zip(cases, query_vectors):
        ranked_documents = sorted(
            (
                (
                    document,
                    calculate_cosine_similarity(
                        vector_a=query_vector,
                        vector_b=document_vector,
                    ),
                )
                for document, document_vector in zip(
                    documents,
                    document_vectors,
                )
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_17b_dense_score_eval
```


**应观察到：** 高分负例可能超过低分正例。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 不能；相似度描述语义邻近，不验证所需事实是否出现。

## 自测与参考答案

1. 能否凭高相似度断言答案存在？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；相似度描述语义邻近，不验证所需事实是否出现。
2. 正例和无答案负例 → 真 Embedding → Top-1 分数 → 范围比较。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“观察正负分数是否交叉”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
