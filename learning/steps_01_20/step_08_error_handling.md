# 08 · 错误处理

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分用户输入错误和上游失败。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/07 正式项目分层](step_07_project_map.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/api/chat.py)：正式模块，关键定义：`chat`, `stream`, `conversation_chat`, `clear_conversation`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
空 message
→ 422；模拟上游异常
→ API 捕获
→ 502
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


**应观察到：** 接口不向客户端暴露内部异常正文。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 调用方需要区分成功与失败；状态码表达接口处理结果，错误细节在服务端排查。

## 自测与参考答案

1. 为什么不把所有错误返回 200？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 调用方需要区分成功与失败；状态码表达接口处理结果，错误细节在服务端排查。
2. 空 message → 422；模拟上游异常 → API 捕获 → 502。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“区分用户输入错误和上游失败”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
