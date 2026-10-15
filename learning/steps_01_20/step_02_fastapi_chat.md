# 02 · 最小 FastAPI 接口

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

把 JSON 请求映射为 Python 对象。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/01 最小模型对话](step_01_basic_chat.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_02_fastapi_chat.py)：学习代码，关键定义：`ChatRequest`, `ChatResponse`, `chat`, `ask`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
POST /chat，message=“什么是 HTTP”
→ ChatRequest
→ chat
→ SDK
→ ChatResponse
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def chat(request: ChatRequest) -> ChatResponse:
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "你是一名简洁、耐心的学习助手。",
            },
            {
                "role": "user",
                "content": request.message,
            },
        ],
    )

    answer = response.choices[0].message.content
    return ChatResponse(
        answer=answer or "模型没有返回内容",
        model=settings.llm_model,
    )
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m uvicorn learning.steps_01_20.step_02_fastapi_chat:app --reload
```

启动后访问 http://127.0.0.1:8000/docs，展开本课接口，按上面的输入提交；结束服务按 Ctrl+C。

**应观察到：** /docs 可提交请求并得到 answer；这是独立教学应用。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- FastAPI 按参数类型调用 Pydantic 校验并构建对象，业务函数随后读取 request.message。

## 自测与参考答案

1. 是谁把 JSON 转成 ChatRequest？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. FastAPI 按参数类型调用 Pydantic 校验并构建对象，业务函数随后读取 request.message。
2. POST /chat，message=“什么是 HTTP” → ChatRequest → chat → SDK → ChatResponse。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“把 JSON 请求映射为 Python 对象”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
