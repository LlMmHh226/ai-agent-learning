# 05 · 字符 n-gram 检索

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

从字面重合实现最小检索。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/04 文本切分](step_04_chunker.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_05_retrieve_top_one.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
物流问题
→ 字符片段集合
→ 与每个 chunk 比较
→ 排序
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
query = "星云机械键盘支持热插拔吗？"
documents = load_markdown_documents()
chunks = split_documents(documents)
results = retrieve(
    query=query,
    chunks=chunks,
    top_k=1,
)

print(f"用户问题：{query}")
print(f"问题的二元字符组：{sorted(build_char_ngrams(query))}")

if results:
    top_result = results[0]
    print(f"第一名：{top_result.document.metadata['chunk_id']}")
    print(f"得分：{top_result.score:.3f}")
    print(top_result.document.content.replace("\n", " "))
else:
    print("没有找到包含相同字符组的 chunk")
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_05_retrieve_top_one
```


**应观察到：** Top-1 指向最相近文档，能解释得分来源。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 字面表达与知识原文不同，n-gram 不具备通用语义理解。

## 自测与参考答案

1. “快递两天没动静”为什么可能漏召回？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 字面表达与知识原文不同，n-gram 不具备通用语义理解。
2. 物流问题 → 字符片段集合 → 与每个 chunk 比较 → 排序。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“从字面重合实现最小检索”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
