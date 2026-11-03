# 10 · 正式RAG接入

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

让API与知识工具共用后端。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [事务更新向量](step_09c_refresh_vectors.md)。 使用环境：.venv + 独立教学数据库。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [核心文件](../../app/rag/knowledge_retriever.py)：按本课数据流查找对应定义。
- [根配置说明](../../docs/database.md)：统一数据库、模型与后端设置。

## 具体输入与执行过程

```text
pgvector后端
→ V4问题向量
→ 数据库Top-K
→ 阈值
→ Prompt/answer/sources
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：启用pgvector后的有效问题访问数据库、真实Embedding和聊天模型。**

```console
python -m uvicorn main:app --reload
```

应观察到：ngram与pgvector显式切换，数据库故障不伪装成无资料。



根.env设置 `EMBEDDING_MODEL=text-embedding-v4`、`EMBEDDING_DIMENSIONS=1536`、`KNOWLEDGE_RETRIEVAL_BACKEND=pgvector`、`PGVECTOR_TOP_K=3`、`PGVECTOR_MIN_SCORE=0.5`，确认知识已入库后重启。每次请求只生成问题向量；文档向量不在提问时重建。完整顺序见 [数据库说明](../../docs/database.md)。

## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 只是教学默认，需用正负例和留出题校准；不同后端的分数不能直接共用。

## 自测与参考答案

1. 0.5阈值是不是最佳值？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 只是教学默认，需用正负例和留出题校准；不同后端的分数不能直接共用。
2. pgvector后端 → V4问题向量 → 数据库Top-K → 阈值 → Prompt/answer/sources。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“让API与知识工具共用后端”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
