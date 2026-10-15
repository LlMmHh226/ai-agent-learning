# 14 · Agent 工具循环

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

串联会话与工具调用。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/13 HTTP 接口测试](step_13_fastapi_test.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/services/llm_service.py)：正式模块，关键定义：`LLMService`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
“查10001物流”
→ 模型提出调用
→ Python 执行
→ tool 回传
→ 最终正文
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    async def chat_with_messages(
            self,
            messages: list[dict[str, str]],
    ) -> str:
        # 使用副本，避免把临时的 tool 消息写入会话历史。
        working_messages: list[dict[str, Any]] = [dict(item) for item in messages]

        for _ in range(MAX_TOOL_ROUNDS):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=working_messages,
                tools=AVAILABLE_TOOLS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                return assistant_message.content or "模型没有返回有效内容"

            working_messages.append(
                assistant_message.model_dump(exclude_none=True)
            )

            for tool_call in assistant_message.tool_calls:
                result = self._execute_tool(
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                )
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_llm_service -v
```


**应观察到：** 第二次请求包含工具结果；Service 最后保存最终回答。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 第一次请求得到工具调用意图；第二次模型读取工具数据生成最终回答。

## 自测与参考答案

1. 一次用户问题为何可能请求模型两次？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 第一次请求得到工具调用意图；第二次模型读取工具数据生成最终回答。
2. “查10001物流” → 模型提出调用 → Python 执行 → tool 回传 → 最终正文。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“串联会话与工具调用”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
