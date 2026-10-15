# 17f · RAG 阶段边界

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

盘点正式链路与实验链路。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17e 证据审计](step_17e_evidence_audit.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/services/rag_service.py)：正式模块，关键定义：`RAGSource`, `RAGResult`, `build_sources`, `RAGService`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
API
→ RAGService
→ n-gram；独立脚本
→ Dense/Hybrid
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


**应观察到：** 能分别指出检索、生成、来源、拒答的实现位置。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不能；本仓库有独立向量实验，但正式问答入口仍使用 n-gram。

## 自测与参考答案

1. 可以声称已部署向量 RAG 吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；本仓库有独立向量实验，但正式问答入口仍使用 n-gram。
2. API → RAGService → n-gram；独立脚本 → Dense/Hybrid。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“盘点正式链路与实验链路”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
