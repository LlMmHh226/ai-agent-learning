# 20c · Edge

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

让后一节点读取前一节点结果。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/20b Node](step_20b_langgraph_node.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_20c_langgraph_edge.py)：学习代码，关键定义：`ReplyState`, `format_answer`, `build_graph`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
lookup
→ 状态更新order_result
→ reply
→ answer
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def format_answer(state: ReplyState) -> dict[str, str]:
    order_result = state["order_result"]
    print("整理回答节点读到的order_result：", order_result)
    if not order_result.get("found"):
        answer = "没有找到该订单。"
    elif order_result.get("tracking_number"):
        answer = f"订单{state['order_id']}的物流单号是{order_result['tracking_number']}。"
    else:
        answer = f"订单{state['order_id']}当前状态为{order_result['status']}，暂无物流单号。"
    return {"answer": answer}
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_20c_langgraph_edge
```


**应观察到：** 已有/不存在订单得到不同文本；回答是Python拼接。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 后继节点读取更新后的整体State，而不是普通位置参数式的返回值串接。

## 自测与参考答案

1. 边会传一个独立的函数返回值吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 后继节点读取更新后的整体State，而不是普通位置参数式的返回值串接。
2. lookup → 状态更新order_result → reply → answer。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“让后一节点读取前一节点结果”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
