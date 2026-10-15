# 14b · 真实工具选择

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

验证模型与工具说明的匹配。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/14 知识库 Tool Loop](step_14_agent_knowledge_loop.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_14b_real_tool_selection.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
商品问题
→ 真实模型
→ search_knowledge_base
→ 回传
→ 回答
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    AVAILABLE_TOOLS,
    DEFAULT_SYSTEM_PROMPT,
    llm_service,
)


query = "星云机械键盘支持热插拔吗？"
messages = [
    {
        "role": "system",
        "content": DEFAULT_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": query,
    },
]

try:
    response = asyncio.run(
        llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=messages,
            tools=AVAILABLE_TOOLS,
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_14b_real_tool_selection
```


**应观察到：** 成功时获得真实工具调用；限流时停止，不写成成功。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 工具名称/描述、传入的问题、模型是否支持工具调用、实际返回的 tool_calls。

## 自测与参考答案

1. 工具没选对先检查什么？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 工具名称/描述、传入的问题、模型是否支持工具调用、实际返回的 tool_calls。
2. 商品问题 → 真实模型 → search_knowledge_base → 回传 → 回答。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“验证模型与工具说明的匹配”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
