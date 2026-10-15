# 19c · 单工具往返

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

手动管理一次工具调用。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/19b LangChain 单次请求](step_19b_langchain_single_call.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_19c_langchain_order_tool.py)：学习代码，关键定义：`execute_order_call`, `ask_order`, `main`, `print_connection_diagnostics`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
订单问题
→ bind_tools
→ AIMessage.tool_calls
→ execute_order_call
→ ToolMessage
→ 第二次模型
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def execute_order_call(tool_call: dict) -> dict[str, object]:
    if tool_call.get("name") != "get_order_status":
        return {"error": "不支持的工具"}
    arguments = tool_call.get("args")
    if not isinstance(arguments, dict) or set(arguments) != {"order_id"}:
        return {"error": "订单查询参数无效"}
    order_id = arguments["order_id"]
    if not isinstance(order_id, str):
        return {"error": "订单编号必须是字符串"}
    return get_order_status(order_id)
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_19c_langchain_order_tool
```


**应观察到：** 合法调用返回订单回答，参数和关联ID有校验。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 这里 args 是已解析字典，原生 function.arguments 是JSON字符串；不要重复解析。

## 自测与参考答案

1. LangChain args 与原生 arguments 有何差别？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 这里 args 是已解析字典，原生 function.arguments 是JSON字符串；不要重复解析。
2. 订单问题 → bind_tools → AIMessage.tool_calls → execute_order_call → ToolMessage → 第二次模型。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“手动管理一次工具调用”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
