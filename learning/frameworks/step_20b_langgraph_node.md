# 20b · Node

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分登记函数与调用函数。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/20a State](step_20a_langgraph_state.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_20b_langgraph_node.py)：学习代码，关键定义：`main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
add_node登记query_order
→ graph.invoke传状态
→ 执行节点
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    builder = StateGraph(OrderState)
    print("1. 准备登记节点，尚未查询订单。")

    # 字符串是图里的步骤名，query_order是不带括号的函数对象。
    builder.add_node("lookup", query_order)
    print("2. 已登记lookup节点，query_order尚未执行。")

    # 连接使用节点名lookup，不使用Python函数名query_order。
    builder.add_edge(START, "lookup")
    builder.add_edge("lookup", END)
    graph = builder.compile()
    print("3. 已创建可执行图，仍未查询订单。")

    initial_state: OrderState = {"order_id": "10002", "order_result": {}}
    print("4. 开始graph.invoke，输入状态：", initial_state)
    final_state = graph.invoke(initial_state)
    print("5. 图执行完成，最终状态：", final_state)

    assert final_state["order_id"] == "10002"
    assert final_state["order_result"]["status"] == "待发货"
    assert final_state["order_result"]["tracking_number"] == ""
    assert initial_state == {"order_id": "10002", "order_result": {}}
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_20b_langgraph_node
```


**应观察到：** 登记时不查询订单，执行图时才运行。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不是；节点名是图内标识，可以与实际Python函数名不同。

## 自测与参考答案

1. 节点名 lookup 等于函数名吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不是；节点名是图内标识，可以与实际Python函数名不同。
2. add_node登记query_order → graph.invoke传状态 → 执行节点。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“区分登记函数与调用函数”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
