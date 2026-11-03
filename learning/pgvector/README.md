# pgvector语义检索与正式接入

[课程总目录](../README.md)

先启用扩展并学会入库与检索，再处理切分、来源与知识更新，最后接入正式RAG。入门默认ngram，配置切换后才使用pgvector。V2历史实验与V4数据库向量不可混用。

- [01 准备向量扩展](step_01_prepare_pgvector.md) — 当前命令只读或预览；写入/生成选项见下文
- [02 建向量表](step_02_enable_and_schema.md) — 当前命令只读或预览；写入/生成选项见下文
- [03 单片段入库](step_03_insert_one_chunk.md) — 当前命令只读或预览；写入/生成选项见下文
- [04 批量入库](step_04_batch_insert.md) — 当前命令只读或预览；写入/生成选项见下文
- [05 问题向量Top-K](step_05_query_topk.md) — 当前命令只读或预览；写入/生成选项见下文
- [06 结果转Prompt](step_06_build_messages.md) — 本地资料演示，无数据库和模型请求
- [07 按资料生成](step_07_generate_answer.md) — 当前命令只读或预览；写入/生成选项见下文
- [08 程序生成sources](step_08_sources.md) — 本地资料演示，无数据库和模型请求
- [09 按章节切分](step_09_section_chunking.md) — 本地资料演示，无数据库和模型请求
- [09B 更新计划](step_09b_refresh_plan.md) — 本地资料演示，无数据库和模型请求
- [09C 事务更新向量](step_09c_refresh_vectors.md) — 当前命令只读或预览；写入/生成选项见下文
- [10 正式RAG接入](step_10_formal_pgvector.md) — 启用pgvector后的有效问题访问数据库、真实Embedding和聊天模型
