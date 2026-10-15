# 11 · RAG HTTP 接口

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

把独立 RAG 服务暴露为接口。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/10 结构化来源](step_10_sources.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_11_rag_api.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
POST /api/rag/chat
→ Schema
→ rag_service.chat
→ 响应
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
client = TestClient(app)
fake_result = RAGResult(
    answer="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
    sources=[
        RAGSource(
            source="shipping.md",
            chunk_id="shipping.md#chunk-0",
            snippet="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
        )
    ],
)

with patch.object(
    rag_service,
    "chat",
    new=AsyncMock(return_value=fake_result),
):
    response = client.post(
        "/api/rag/chat",
        json={"message": "物流轨迹超过 48 小时没有更新怎么办？"},
    )

print(f"HTTP 状态码：{response.status_code}")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_11_rag_api
```


**应观察到：** 进程内模拟生成，返回 answer 与 sources 结构。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不是；调用方请求 URL，FastAPI 匹配路由；工具选择发生在 Agent 内部。

## 自测与参考答案

1. 选择 HTTP 入口的是模型吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不是；调用方请求 URL，FastAPI 匹配路由；工具选择发生在 Agent 内部。
2. POST /api/rag/chat → Schema → rag_service.chat → 响应。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“把独立 RAG 服务暴露为接口”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
