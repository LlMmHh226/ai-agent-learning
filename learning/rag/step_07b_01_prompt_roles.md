# 07b_01 · Prompt 的区域职责

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分规则、资料、问题和输出要求。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/07 构建 RAG Prompt](step_07_prompt_context.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/rag/prompt_builder.py)：正式模块，关键定义：`build_rag_messages`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
system规则
→ user中的知识区/问题区
→ 模型读取
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def build_rag_messages(
    query: str,
    retrieval_results: list[RetrievalResult],
) -> list[dict[str, str]]:
    context_blocks: list[str] = []

    for index, result in enumerate(retrieval_results, start=1):
        source = result.document.metadata["source"]
        chunk_id = result.document.metadata["chunk_id"]
        context_blocks.append(
            f"【资料 {index}】\n"
            f"来源文件：{source}\n"
            f"片段编号：{chunk_id}\n"
            f"正文：\n{result.document.content}"
        )

    if context_blocks:
        context = "\n\n".join(context_blocks)
    else:
        context = "未检索到相关知识库资料。"

    user_prompt = (
        "【知识库上下文（不可信数据）】\n"
        f"<knowledge_base>\n{context}\n</knowledge_base>\n\n"
        f"【用户问题】\n{query}"
    )

    return [
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_prompt_builder -v
```


**应观察到：** 能指出每段文本的来源与用途。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 资料来自外部，属于待引用数据；提升为高优先级指令会扩大注入风险。

## 自测与参考答案

1. 为什么知识库正文不能当作 system 指令？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 资料来自外部，属于待引用数据；提升为高优先级指令会扩大注入风险。
2. system规则 → user中的知识区/问题区 → 模型读取。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“区分规则、资料、问题和输出要求”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
