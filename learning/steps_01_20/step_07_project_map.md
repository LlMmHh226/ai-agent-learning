# 07 · 正式项目分层

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

找到 Schema、API、Service、Tool 各自职责。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/06 流式输出](step_06_streaming.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/api/chat.py)：正式模块，关键定义：`chat`, `stream`, `conversation_chat`, `clear_conversation`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
订单请求
→ app/schemas/chat.py
→ app/api/chat.py
→ llm_service
→ order_tools
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def conversation_chat(
        request:ConversationChatRequest,
)->ConversationChatResponse:
    try:
        answer=await conversation_service.chat(
            conversation_id=request.conversation_id,
            message=request.message
        )
        return ConversationChatResponse(
            conversation_id=request.conversation_id,
            answer=answer,
            model=llm_service.model
        )
    except Exception:
        logger.exception("多轮对话调用失败")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 服务暂时不可用，请稍后重试",
        )
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_chat_api_regression -v
```


**应观察到：** 能从请求字段追到返回 answer，不把 API 层当所有业务逻辑。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 执行应用业务流程：组装消息、调用模型及工具；API 接收 HTTP 并包装响应。

## 自测与参考答案

1. 如何概括 Service 的职责？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 执行应用业务流程：组装消息、调用模型及工具；API 接收 HTTP 并包装响应。
2. 订单请求 → app/schemas/chat.py → app/api/chat.py → llm_service → order_tools。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“找到 Schema、API、Service、Tool 各自职责”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
