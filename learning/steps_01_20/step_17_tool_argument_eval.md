# 17 · 工具参数评测

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

检查参数的类型与业务含义。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/16 工具选择评测](step_16_tool_selection_eval.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_17_tool_argument_eval.py)：学习代码，关键定义：`ArgumentEvalCase`, `main`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
订单问题
→ arguments
→ JSON 解析
→ order_id 对比
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def main() -> None:
    settings = get_settings()
    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        max_retries=0,
        timeout=20.0,
    )

    passed = 0
    completed = 0

    for index, case in enumerate(CASES, start=1):
        try:
            actual_tool, arguments_text = await select_tool(
                client=client,
                model=settings.llm_model,
                question=case.question,
            )
        except APIError as error:
            print(f"\n用例 {index}：跳过（API错误 {error.status_code}）")
            continue

        completed += 1

        try:
            actual_arguments = json.loads(arguments_text)
        except json.JSONDecodeError:
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.steps_01_20.step_17_tool_argument_eval
```


**应观察到：** 记录参数正确和错误案例，不执行真实写操作。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 可能查询另一笔订单；名称与参数需要分别评估。

## 自测与参考答案

1. 名称正确但 order_id 错误会怎样？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 可能查询另一笔订单；名称与参数需要分别评估。
2. 订单问题 → arguments → JSON 解析 → order_id 对比。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“检查参数的类型与业务含义”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
