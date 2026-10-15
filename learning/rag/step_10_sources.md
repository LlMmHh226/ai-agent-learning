# 10 · 结构化来源

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

从真实检索结果构造返回对象。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/09 程序级拒答](step_09_reliable_refusal.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_10_sources.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
retrieve
→ build_sources
→ RAGSource
→ RAGResult
→ asdict
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
query = "物流轨迹超过 48 小时没有更新怎么办？"

retrieval_results = retrieve(
    query=query,
    chunks=rag_service.chunks,
    top_k=rag_service.top_k,
    min_score=rag_service.min_score,
)
sources = build_sources(retrieval_results=retrieval_results)

# 本脚本不调用模型，用预期正文专注观察正式返回类型和 sources。
result = RAGResult(
    answer="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
    sources=sources,
)

print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_10_sources
```


**应观察到：** 打印 answer/sources JSON，来源包含文件、chunk_id、片段。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不应；从检索对象构造可避免模型编造不存在的文件名。

## 自测与参考答案

1. 来源字段应由模型自由填写吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不应；从检索对象构造可避免模型编造不存在的文件名。
2. retrieve → build_sources → RAGSource → RAGResult → asdict。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“从真实检索结果构造返回对象”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
