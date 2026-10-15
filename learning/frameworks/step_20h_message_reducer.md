# 20h · Reducer

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

比较替换和按ID合并。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/20g 节点失败](step_20g_node_failure.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_20h_message_reducer.py)：学习代码，关键定义：`ReplaceState`, `MergeState`, `reply_node`, `build_graph`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
旧messages+新消息
→ 默认替换或add_messages
→ 新状态
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def reply_node(state: ReplaceState) -> dict[str, list[AIMessage]]:
    question = state["messages"][-1].content
    reply = AIMessage(content=f"模拟回答：收到你的问题“{question}”。", id="a2")
    return {"messages": [reply]}
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_20h_message_reducer
```


**应观察到：** 默认只保留更新列表；合并保留旧消息，同ID更新。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不是；有相同消息ID时会更新已有消息。

## 自测与参考答案

1. add_messages 是否永远只append？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不是；有相同消息ID时会更新已有消息。
2. 旧messages+新消息 → 默认替换或add_messages → 新状态。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“比较替换和按ID合并”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
