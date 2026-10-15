# 08 · RAGService

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

将检索与生成组成服务。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/07b_05 答案与来源](step_07b_05_answer_and_sources.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_08_rag_service.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
物流问题
→ RAGService.chat
→ retrieve
→ build_rag_messages
→ complete_messages
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
query = "物流轨迹超过 48 小时没有更新怎么办？"

try:
    result = asyncio.run(rag_service.chat(query=query))
    print(f"用户问题：{query}")
    print(f"模型回答：{result.answer}")
    print(f"来源数量：{len(result.sources)}")
except RateLimitError:
    print("模型服务返回 429 限流，本次不再重复调用，请稍后重试。")
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_08_rag_service
```


**应观察到：** 真实模型返回 answer，同时 Python 构造 sources。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 独立 RAG 已先检索，无需再让模型选择检索工具；直接按资料生成即可。

## 自测与参考答案

1. 为什么用 complete_messages 而非工具循环？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 独立 RAG 已先检索，无需再让模型选择检索工具；直接按资料生成即可。
2. 物流问题 → RAGService.chat → retrieve → build_rag_messages → complete_messages。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“将检索与生成组成服务”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
