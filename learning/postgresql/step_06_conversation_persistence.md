# PostgreSQL 06：会话持久化与版本冲突

## 学习目标

让两次独立的 Python 进程读取同一个会话快照，并观察为什么旧版本不能覆盖新版本。

## 前置知识

先学 [第三课的参数化查询](step_03_python_order_lookup.md) 和 [原生会话的资料流](../../learning/steps_01_20/README.md)。需要真实数据库时再按 [数据库说明](../../docs/database.md) 启动教学容器。

## 文件职责

- [建表 SQL](exercises/step_06_conversation_schema.sql)：在 `public.lesson_conversations` 保存会话 ID、问答数组、事实对象和 UUID 版本号。
- [教学脚本](step_06_conversation_persistence.py)：参数化读写同一行，使用 `RETURNING` 判断写入是否成功；只连接本机教学库 `agent_learning`。
- [正式会话服务](../../app/services/conversation_service.py)：用来对照内存版的历史与事实。本课脚本不接管这条 HTTP 路径。

## 具体输入与执行过程

以独立样例 `lesson-demo-06` 为例。第一次写入一对问答和 `last_order_id=10001` → `INSERT` 创建新版本 → 新进程按会话 ID `SELECT` → 在一个事务中按「ID + 读取时的版本」更新 → 另一个持旧版本的写入匹配零行，被判定为冲突。对话文本不会经过模型；工具消息也不进这个教学快照。

## 运行与预期结果

先在基础环境离线预览，无需 `.env` 或数据库：

```console
python -m learning.postgresql.step_06_conversation_persistence
```

要验证真实存储，按 [数据库说明](../../docs/database.md) 配置容器和根目录 `.env`。本课固定使用默认库名 `agent_learning`、用户 `learner`，端口读取 `POSTGRES_PORT`。以下命令在 Windows PowerShell、macOS 和 Linux 均从仓库根目录执行；每一条 Python 命令都是新的进程。这个模式仅连接本机教学 PostgreSQL，不调用模型。

```console
docker compose --env-file .env -f learning/postgresql/compose.yaml exec -T postgres psql -U learner -d agent_learning -v ON_ERROR_STOP=1 -f /learning/exercises/step_06_conversation_schema.sql
python -m learning.postgresql.step_06_conversation_persistence --mode write --conversation-id lesson-demo-06
python -m learning.postgresql.step_06_conversation_persistence --mode read --conversation-id lesson-demo-06
python -m learning.postgresql.step_06_conversation_persistence --mode conflict --conversation-id lesson-demo-06
```

预期先看到新 `revision`，再读到示例问答与订单事实，最后看到旧版本被拒绝。`conflict` 用两个顺序写入重现「两个请求都读到旧版本」的关键条件。练习完清理这个示例 ID：

```console
python -m learning.postgresql.step_06_conversation_persistence --mode clear --conversation-id lesson-demo-06
python -m learning.postgresql.step_06_conversation_persistence --mode read --conversation-id lesson-demo-06
```

清理后读取应显示 `null`。同学共用一套教学库时，请用各自独立的 `lesson-` 开头的标识。

## 常见错误

- 容器已启动却查不到教学表：这张表需执行上面的 SQL；订单表存在并不意味着它已创建。
- 把 `revision` 当自增轮次：这里它是并发写入的令牌，每次保存重新生成。
- 连接失败：先看教学容器是否健康、`.env` 端口与密码是否对应；运行默认预览不需要解决这些配置。

## 自测与参考答案

两个进程都从版本 A 加一轮消息，为什么仅仅开启事务仍可能丢掉一轮？保存时只有订单号事实、没有当时的问答，有什么缺口？

<details>
<summary>参考答案</summary>

两个事务各自拿着完整的旧快照，若更新仅按会话 ID，后提交者可覆盖先提交者的新增内容。增加 `revision = A` 条件可以识别冲突。事实可以辅助补全指代，问答才提供交流上下文；两者应按同一快照提交。

</details>
