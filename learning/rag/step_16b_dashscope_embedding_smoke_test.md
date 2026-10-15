# 16b · 百炼 Embedding

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

验证批量文本到向量。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/16 检查 Embedding 支持](step_16_check_embedding_support.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_16b_dashscope_embedding_smoke_test.py)：学习代码，关键定义：`cosine_similarity`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
两段文本
→ TextEmbedding.call
→ embeddings
→ 检查数量与1536维
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))
    return dot_product / (magnitude_a * magnitude_b)
```

## 运行与预期结果

**访问范围：真实外部请求（可能收费）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_16b_dashscope_embedding_smoke_test
```


**应观察到：** text-embedding-v2 正常返回两条等长向量，前五个仅预览。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 401/403检查模型权限；429停止本次实验，稍后再试；连接错误先核对地址和网络。不要把密钥贴进Issue。
- 本项目用它校验返回长度；v2 不通过该设置改变模型维度。

## 自测与参考答案

1. EMBEDDING_DIMENSIONS 是否改变 v2 输出？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 本项目用它校验返回长度；v2 不通过该设置改变模型维度。
2. 两段文本 → TextEmbedding.call → embeddings → 检查数量与1536维。涉及模型的箭头访问外部服务，其余数据组装、校验与业务工具在本地执行。

</details>

## 完成标准

- 能解释“验证批量文本到向量”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
