# 19b · LangChain 单次请求

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

追踪 AIMessage 与正文返回。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/19a LangChain 接口映射](step_19a_langchain_interfaces.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_19b_langchain_single_call.py)：学习代码，关键定义：`ask_customer_service`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
question
→ HumanMessage
→ ainvoke
→ AIMessage
→ reply.content
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def ask_customer_service(question: str) -> str:
    settings = get_settings()
    model = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=30,
        max_retries=0,
    )
    messages = [
        SystemMessage(content="你是一名电商客服，请用一句简短的中文问候回答。"),
        HumanMessage(content=question),
    ]
    print("question：", question)
    print("messages类型：", [type(message).__name__ for message in messages])
    print("开始请求模型，本示例不自动重试……")
    reply = await model.ainvoke(messages)
    print("reply类型：", type(reply).__name__)
    print("reply.content类型：", type(reply.content).__name__)
    if not isinstance(reply.content, str) or not reply.content.strip():
        raise ValueError("本步预期非空文本回答，实际输出不符合要求。")
    return reply.content
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_19b_langchain_single_call
```


**应观察到：** 真实模型返回非空文本；本公开版不自动重试。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- str只含正文，AIMessage还可能携带工具调用和元数据。

## 自测与参考答案

1. 函数返回的 str 与 AIMessage 有何区别？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. str只含正文，AIMessage还可能携带工具调用和元数据。
2. question → HumanMessage → ainvoke → AIMessage → reply.content。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“追踪 AIMessage 与正文返回”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
