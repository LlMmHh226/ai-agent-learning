# 15d_recall · Recall@K

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

衡量相关资料有没有被找回。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/15c 余弦相似度](step_15c_cosine_similarity.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_15d_recall_at_k.py)：学习代码，关键定义：`calculate_recall_at_k`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
人工相关来源集合+Top-K
→ 交集数/相关总数
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def calculate_recall_at_k(
    cases: list[tuple[str, str]],
    chunks: list[Document],
    k: int,
) -> float:
    if not cases:
        raise ValueError("评测用例不能为空")
    if k <= 0:
        raise ValueError("k 必须大于 0")

    hit_count = 0

    for question, expected_source in cases:
        results = retrieve(
            query=question,
            chunks=chunks,
            top_k=k,
            min_score=0.0,
        )
        returned_sources = [
            result.document.metadata["source"]
            for result in results
        ]
        hit = expected_source in returned_sources
        if hit:
            hit_count += 1

        print(
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_15d_recall_at_k
```


**应观察到：** 改变 K 后计算召回，分母不随返回量变化。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 人工标注的全部相关项数量，不是返回结果数量。

## 自测与参考答案

1. Recall 的分母是什么？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 人工标注的全部相关项数量，不是返回结果数量。
2. 人工相关来源集合+Top-K → 交集数/相关总数。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“衡量相关资料有没有被找回”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
