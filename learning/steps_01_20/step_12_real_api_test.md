# 12 · 真实 API 集成检查

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分本地检查与外部连通性。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/11 模拟模型测试](step_11_mock_model_test.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_12_real_api_test.py)：学习代码，关键定义：`RealAPIIntegrationTests`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
配置真实模型
→ RealAPIIntegrationTests
→ 请求
→ 非空文本
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    async def test_real_model_returns_text(self) -> None:
        # Arrange：创建使用 .env 配置的真实模型服务。
        service = LLMService()

        # Act：实际发起网络请求。
        answer = await service.chat(
            "请只用一句简短的话回答：API连接测试成功。"
        )

        # 方便学习时直接观察真实模型返回了什么。
        print(f"\n真实模型回答：{answer}")

        # Assert：真实模型措辞可能变化，所以只检查类型和非空内容。
        self.assertIsInstance(answer, str)
        self.assertTrue(answer.strip())
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.steps_01_20.step_12_real_api_test
```


**应观察到：** 真实请求可得到正文；鉴权或限流时应停止排查。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 它依赖密钥、网络和供应商额度，不稳定且可能收费；CI 使用本地模拟。

## 自测与参考答案

1. 为何这一步不放进默认 CI？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 它依赖密钥、网络和供应商额度，不稳定且可能收费；CI 使用本地模拟。
2. 配置真实模型 → RealAPIIntegrationTests → 请求 → 非空文本。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“区分本地检查与外部连通性”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
