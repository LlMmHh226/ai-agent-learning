# 16 · 检查 Embedding 支持

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

先核实服务能力再写检索。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/15f 幻觉排查](step_15f_hallucination.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_16_check_embedding_support.py)：学习代码，关键定义：`check_embedding_candidates`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
聊天配置
→ models.list
→ 按名称筛选候选
→ 继续核对供应商文档
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def check_embedding_candidates() -> None:
    settings = get_settings()
    client = AsyncOpenAI(
        max_retries=0,
        timeout=30,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )

    try:
        model_page = await client.models.list()
        model_ids = [model.id for model in model_page.data]
        candidates = [
            model_id
            for model_id in model_ids
            if any(
                hint in model_id.lower()
                for hint in EMBEDDING_NAME_HINTS
            )
        ]

        print(f"服务返回模型数量：{len(model_ids)}")
        print(f"名称疑似 Embedding 的候选：{candidates}")
        if not candidates:
            print(
                "模型列表中未发现明显候选；这不能单独证明服务不支持，"
                "还需要服务方文档或明确模型名。"
            )
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_16_check_embedding_support
```


**应观察到：** 仅列出疑似Embedding候选；不能仅凭名称证明支持，尚未发送Embedding请求。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 不能；模型、接口和权限可能分别配置，需要独立确认。

## 自测与参考答案

1. 聊天 API 可用就能做 Embedding 吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；模型、接口和权限可能分别配置，需要独立确认。
2. 聊天配置 → models.list → 按名称筛选候选 → 继续核对供应商文档。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“先核实服务能力再写检索”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
