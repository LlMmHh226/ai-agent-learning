# 07b_03 · 资料不足

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

识别空上下文与缺失事实。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/07b_02 Grounding](step_07b_02_grounding_rule.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_07b_03_missing_context.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
“你们公司的董事长是谁？”
→ 检索资料
→ 观察拒答提示
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
query = "你们公司的董事长是谁？"

documents = load_markdown_documents()
chunks = split_documents(
    documents=documents,
    chunk_size=10_000,
    overlap=0,
)
retrieval_results = retrieve(
    query=query,
    chunks=chunks,
    top_k=1,
)
messages = build_rag_messages(
    query=query,
    retrieval_results=retrieval_results,
)

print(f"用户问题：{query}")
print(f"检索结果数：{len(retrieval_results)}")

for message in messages:
    print(f"\n===== {message['role']} =====")
    print(message["content"])
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_07b_03_missing_context
```


**应观察到：** 提示要求说明无法确认，避免补写营销规则。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不同；后者可能分数很高，需要核对回答所需事实。

## 自测与参考答案

1. “没搜到”和“文档相关但没答案”相同吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不同；后者可能分数很高，需要核对回答所需事实。
2. “你们公司的董事长是谁？” → 检索资料 → 观察拒答提示。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“识别空上下文与缺失事实”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
