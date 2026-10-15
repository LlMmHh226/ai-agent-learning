# 20k · 会话接图

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

用薄适配返回正文字符串。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/20j 原生与图对照](step_20j_native_graph_comparison.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_20k_graph_conversation.py)：学习代码，关键定义：`make_graph_chat`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
ConversationService消息
→ make_graph_chat
→ convert_to_messages
→ ainvoke
→ 最后正文
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def make_graph_chat(graph):
    async def graph_chat_with_messages(messages: list[dict[str, str]]) -> str:
        """messages来自ConversationService；图返回State后取正文交回会话服务。

        convert_to_messages把role/content字典转为消息对象，不替代facts组装。
        不额外添加system，否则可能丢失或重复服务已组装的订单背景。
        """
        result = await graph.ainvoke(
            {"messages": convert_to_messages(messages)},
            config={"recursion_limit": 6},
        )
        final_message = result["messages"][-1]
        if not isinstance(final_message, AIMessage) or final_message.tool_calls:
            raise ValueError("图没有返回最终回答消息。")
        if not isinstance(final_message.content, str) or not final_message.content.strip():
            raise ValueError("图没有返回非空正文。")
        return final_message.content
    return graph_chat_with_messages
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_20k_graph_conversation
```


**应观察到：** 会话仍负责facts与history；临时替换只在with内有效。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 没有；facts仍由ConversationService读取和组装，图处理已准备的消息。

## 自测与参考答案

1. 图是否自动代替原会话服务的facts？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 没有；facts仍由ConversationService读取和组装，图处理已准备的消息。
2. ConversationService消息 → make_graph_chat → convert_to_messages → ainvoke → 最后正文。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“用薄适配返回正文字符串”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
