# 11 · 模拟模型测试

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

隔离 SDK 与业务处理。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/10 参数化测试](step_10_parameterized_test.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_11_mock_model_test.py)：学习代码，关键定义：`LLMServiceMockTests`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
模拟 response
→ LLMService.chat
→ 取正文
→ 断言消息参数
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    async def test_normal_chat_without_real_api(self) -> None:
        # Arrange：准备一个与 SDK 返回结构相似的假响应。
        fake_message = SimpleNamespace(
            content="这是模拟的模型回答",
            tool_calls=[],
        )
        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(message=fake_message),
            ]
        )

        # AsyncMock 模拟异步的 create() 方法。
        create_mock = AsyncMock(return_value=fake_response)

        service = LLMService()
        service.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=create_mock,
                )
            )
        )

        # Act：调用真正的 LLMService，但它内部访问的是假客户端。
        answer = await service.chat("你好")

        # Assert：检查服务返回值。
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.steps_01_20.step_11_mock_model_test
```


**应观察到：** 无需网络验证消息构造与正文提取。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不能；它只证明程序面对所模拟响应时的处理逻辑。

## 自测与参考答案

1. Mock 成功能证明真实模型表现吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；它只证明程序面对所模拟响应时的处理逻辑。
2. 模拟 response → LLMService.chat → 取正文 → 断言消息参数。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“隔离 SDK 与业务处理”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
