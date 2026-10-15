# 04 · 文本切分

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

理解 chunk_size 与 overlap。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/03 文档加载](step_03_document_loader.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_04_split_documents.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
Document
→ split_documents
→ 多个带 chunk_id 的 Document
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
documents = load_markdown_documents()
chunks = split_documents(
    documents=documents,
    chunk_size=120,
    overlap=20,
)

print(f"原始文档数：{len(documents)}")
print(f"切分后的 chunk 数：{len(chunks)}")

for chunk in chunks:
    print(
        f"{chunk.metadata['chunk_id']} "
        f"长度={len(chunk.content)} "
        f"来源={chunk.metadata['source']}"
    )
    print(chunk.content.replace("\n", " "))
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_04_split_documents
```


**应观察到：** 长文切成多块，每块保留来源；短文可能只有一块。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 保留边界上下文，但增加重复内容、索引大小与检索噪声。

## 自测与参考答案

1. overlap 的代价是什么？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 保留边界上下文，但增加重复内容、索引大小与检索噪声。
2. Document → split_documents → 多个带 chunk_id 的 Document。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“理解 chunk_size 与 overlap”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
