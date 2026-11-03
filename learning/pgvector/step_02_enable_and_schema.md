# 02 · 建向量表

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

把正文、来源与向量一起保存。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [准备向量扩展](step_01_prepare_pgvector.md)。 使用环境：.venv + 独立教学数据库。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [核心文件](step_02_schema.sql)：按本课数据流查找对应定义。
- [根配置说明](../../docs/database.md)：统一数据库、模型与后端设置。

## 具体输入与执行过程

```text
CREATE EXTENSION
→ knowledge_chunks
→ vector(1536)
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：当前命令只读或预览；写入/生成选项见下文。**

```console
docker compose --env-file .env -f learning/postgresql/compose.yaml exec -T postgres psql -U learner -d agent_learning -v ON_ERROR_STOP=1 -f /learning/pgvector/step_02_schema.sql
```

应观察到：表结构明确向量维度，不预填任何私有向量。





## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 不能；维度相同的不同模型空间也不兼容，本课程统一V4文档与问题向量。

## 自测与参考答案

1. 同为1536维就一定能混用吗？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 不能；维度相同的不同模型空间也不兼容，本课程统一V4文档与问题向量。
2. CREATE EXTENSION → knowledge_chunks → vector(1536)。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“把正文、来源与向量一起保存”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
