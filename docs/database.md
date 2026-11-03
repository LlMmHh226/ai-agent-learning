# 从演示数据到PostgreSQL与pgvector

[首页](../README.md) · [PostgreSQL课程](../learning/postgresql/README.md) · [pgvector课程](../learning/pgvector/README.md)

## 入门与进阶的配置

| 设置 | 入门默认 | 进阶选择 |
| --- | --- | --- |
| ORDER_STORAGE_BACKEND | demo：三笔虚构订单，无数据库 | postgres：从自己的教学库读取 |
| KNOWLEDGE_RETRIEVAL_BACKEND | ngram：本地Markdown检索 | pgvector：V4问题向量＋数据库余弦Top-K |
| EMBEDDING_MODEL | text-embedding-v2：历史向量实验 | text-embedding-v4：本教程数据库向量 |
| EMBEDDING_DIMENSIONS | 1536 | 1536；同维度不代表不同模型可以混用 |

模式必须显式配置；选了数据库模式但数据库失败时，返回服务错误，不会自动回到演示数据。启动后修改.env需要重启服务。

## 创建独立教学库

先完成Docker安装与hello-world课程。在根目录.env填写自己的本地密码及以下配置：

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=25432
POSTGRES_DB=agent_learning
POSTGRES_USER=learner
POSTGRES_PASSWORD=choose-a-local-password
```

将密码占位值换成自己的值。所有命令在仓库根目录执行，Windows PowerShell与macOS/Linux使用相同Docker命令：

```console
docker compose --env-file .env -f learning/postgresql/compose.yaml config --quiet
docker compose --env-file .env -f learning/postgresql/compose.yaml up -d --wait
docker compose --env-file .env -f learning/postgresql/compose.yaml ps
```

Compose使用官方pgvector/PostgreSQL17镜像、独立项目名与命名卷。默认本机25432映射容器5432。首次初始化卷时，init目录创建三笔虚构订单；以后重启不会自动重建数据。若端口占用，可修改POSTGRES_PORT；不要为腾端口直接停止来源不明的其他数据库。

先运行Python查询，再切正式订单后端：

```console
python -m learning.postgresql.step_03_python_order_lookup --order-id 10001
python -m learning.postgresql.step_03_python_order_lookup --order-id 99999
```

前者返回四字段字典，后者返回null。确认后在.env设置 `ORDER_STORAGE_BACKEND=postgres`，重启FastAPI，再测试正式订单接口。根.env被应用、学习查询和Compose共用，不需要复制维护者的连接配置。

## 准备向量表

```console
docker compose --env-file .env -f learning/postgresql/compose.yaml exec -T postgres psql -U learner -d agent_learning -v ON_ERROR_STOP=1 -f /learning/pgvector/step_02_schema.sql
```

自定义了用户或库名时同步修改命令中的对应值。建表脚本启用vector扩展并创建空knowledge_chunks表，不包含维护者的向量。它不会为已存在的不同维度表执行自动迁移。

在.env中设置V4与1536维，并填入自己百炼账号的DASHSCOPE_API_KEY。历史V2实验生成的向量不能写入这套V4检索数据后混用。

```dotenv
EMBEDDING_PROVIDER=dashscope
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_DIMENSIONS=1536
DASHSCOPE_API_KEY=your-dashscope-api-key
```

## 按课程顺序理解向量写入

单片段、批量和问题检索课程分别提供preview与实际执行选项。preview是否访问数据库以各课说明为准。写向量会把文档发送给Embedding服务；query检索会发送问题，二者都可能收费。

首次只想准备正式检索数据时，建议直接使用9C的章节更新流程，而不先写旧chunk版本：

```console
python -m learning.pgvector.step_09_section_chunking --split
python -m learning.pgvector.step_09c_refresh_vectors --preview
```

当前三篇示例按章节切为7段。确认本地候选、目标来源、库中现状和模型配置后，才执行：

```console
python -m learning.pgvector.step_09c_refresh_vectors --write
```

它先备份，再生成新向量，在同一事务中写新停旧，核对订单未变并独立回读。运行中若失败，先用preview核对状态，不直接反复付费重跑。generated_vectors、备份和收据只留本地，已被Git忽略。若你先完成了3/4步，旧chunk会在同一来源范围的更新计划中被替换；不会删除其他来源记录。

## 正式启用pgvector

知识入库并核对后，在.env设置：

```dotenv
KNOWLEDGE_RETRIEVAL_BACKEND=pgvector
PGVECTOR_TOP_K=3
PGVECTOR_MIN_SCORE=0.5
```

重启 `python -m uvicorn main:app --reload`。`POST /api/rag/chat` 与Agent知识工具现在共用检索入口：V4 query向量 → 数据库 `<=>` 升序Top-K → 1-distance → 阈值 → 原有Prompt/answer/sources。资料不足与服务故障是不同结果，不静默改用n-gram。

0.5是教学默认，尚未有广泛校准。阈值放行不等于证据充分；无答案问题可能召回相关产品背景并返回sources，仍需审核回答是否明确无法确认。

## 停止与保留数据

```console
docker compose --env-file .env -f learning/postgresql/compose.yaml stop
```

停止会保留命名卷。`down -v`会删除卷，不属于普通停止步骤。更改POSTGRES密码配置不会自动改变已初始化数据库中的密码；已有卷需按数据库账号管理方式处理，不能靠反复重建容器猜测修复。
