# 16i_02 · 正式接入决策

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

将实验结果与上线条件分开。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/16i_01 向量库决策](step_16i_01_vector_database_decision.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/services/rag_service.py)：正式模块，关键定义：`RAGSource`, `RAGResult`, `build_sources`, `RAGService`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
实验指标
→ 无答案风险
→ 保留现有 RAGService
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    async def chat(self, query: str) -> RAGResult:
        retrieval_results = retrieve(
            query=query,
            chunks=self.chunks,
            top_k=self.top_k,
            min_score=self.min_score,
        )
        if not retrieval_results:
            return RAGResult(
                answer=RAG_INSUFFICIENT_CONTEXT_RESPONSE,
                sources=[],
            )

        messages = build_rag_messages(
            query=query,
            retrieval_results=retrieval_results,
        )
        answer = await llm_service.complete_messages(messages=messages)
        sources = build_sources(retrieval_results=retrieval_results)
        return RAGResult(
            answer=answer,
            sources=sources,
        )
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_rag_service -v
```


**应观察到：** Dense/Hybrid 可独立使用，正式入口仍 n-gram。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 还需拒答、来源、错误处理、接口回归与实际需求验证。

## 自测与参考答案

1. 实验召回更高为何不能立即替换正式服务？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 还需拒答、来源、错误处理、接口回归与实际需求验证。
2. 实验指标 → 无答案风险 → 保留现有 RAGService。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“将实验结果与上线条件分开”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
