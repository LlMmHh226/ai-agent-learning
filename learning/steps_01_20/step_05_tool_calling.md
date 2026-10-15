# 05 · 第一次工具调用

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分模型提出调用与 Python 执行。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/04 多轮会话](step_04_conversation_memory.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_05_tool_calling.py)：学习代码，关键定义：`ChatRequest`, `ChatResponse`, `execute_tool`, `chat`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
“请查订单10001”
→ Tool Call
→ execute_tool
→ get_order_status
→ tool 消息
→ 模型回答
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def execute_tool(name: str, arguments: str) -> dict[str, object]:
    if name != "get_order_status":
        return {"error": f"不支持的工具：{name}"}

    try:
        parsed_arguments = json.loads(arguments)
        order_id = parsed_arguments["order_id"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return {"error": "订单查询参数无效"}

    if not isinstance(order_id, str):
        return {"error": "订单编号必须是字符串"}

    return get_order_status(order_id)
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m uvicorn learning.steps_01_20.step_05_tool_calling:app --reload
```

启动后访问 http://127.0.0.1:8000/docs，展开本课接口，按上面的输入提交；结束服务按 Ctrl+C。

**应观察到：** 响应 used_tool 为 true，订单数据来自本地演示订单。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 原生 SDK 的 function.arguments 是 JSON 字符串，需要解析为字典才能取 order_id。

## 自测与参考答案

1. arguments 为什么需要 json.loads？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 原生 SDK 的 function.arguments 是 JSON 字符串，需要解析为字典才能取 order_id。
2. “请查订单10001” → Tool Call → execute_tool → get_order_status → tool 消息 → 模型回答。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“区分模型提出调用与 Python 执行”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
