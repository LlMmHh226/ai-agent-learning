# 19e · 工具对象往返

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

用工具对象替换手写调度。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/19d 工具对象](step_19d_langchain_tool_object.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_19e_tool_object_roundtrip.py)：学习代码，关键定义：`execute_tool_object`, `ask_order`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
模型 Tool Call
→ lookup_order.ainvoke
→ ToolMessage
→ 模型正文
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def execute_tool_object(tool_call: dict) -> dict[str, object]:
    if tool_call.get("name") != lookup_order.name:
        return {"error": "不支持的工具"}
    arguments = tool_call.get("args")
    # 保留19C只接受order_id字段的约束；@tool默认不等于禁止额外字段。
    if not isinstance(arguments, dict) or set(arguments) != {"order_id"}:
        return {"error": "订单查询参数无效"}
    try:
        return lookup_order.invoke(arguments)
    except ValidationError:
        return {"error": "订单查询参数类型无效"}
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_19e_tool_object_roundtrip
```


**应观察到：** 真实入口访问模型；本地测试模拟模型而实际执行工具。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 此步骤需要；只有使用运行器或ToolNode时框架才接管更多流程。

## 自测与参考答案

1. 工具对象接入后仍需手动回传结果吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 此步骤需要；只有使用运行器或ToolNode时框架才接管更多流程。
2. 模型 Tool Call → lookup_order.ainvoke → ToolMessage → 模型正文。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“用工具对象替换手写调度”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
