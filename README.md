## 说明

这个项目是我跟着gpt一步一步学习的。从最初调用大模型，到工具调用、RAG、上下文工程，再到 LangChain 和 LangGraph，后续加入mcp，PostgreSQL，评测等

项目中的很多练习来自我真实的学习过程，包括做过的题、遇到的问题，以及反复梳理过的知识点。AI 帮助我讲解概念、编写和修改代码、设计练习以及整理文档。这份项目记录了我如何借助 AI 学习和实践。

为了方便其他人自学，公开版本重新整理了课程结构，并补充了运行说明、自测题和参考答案。因此，公开版并非个人学习对话的原样记录，也不代表其中每一道题都已经由我独立完成。


# 从零读懂 AI 客服 Agent

一套中文、可运行、可逐步跟踪的 AI Agent / Python 后端教程。以同一个电商客服为例，从原生 Python 工具循环出发，学习 RAG、上下文工程，再对照 LangChain 和 LangGraph，并继续实践 MCP、效果评测、PostgreSQL 与 pgvector。

**先跑通真实模型的一句话回答，再理解每一步发生了什么。** 本仓库包含 146 节分步讲义、对应代码、自测题和折叠参考答案。

## 适合谁

适合已了解变量、函数、列表和字典，正在学习 Python 后端或从 Java 等语言转向 AI 应用开发的读者。不要求事先掌握 Agent 框架。遇到语法问题可先读 [代码阅读指南](docs/code-reading.md)。

完成课程后，你应能追踪“HTTP 请求 → 会话与事实 → 模型 → 工具 → 最终回答”，解释 RAG 的召回、拒答与来源，区分原生循环与框架接管的职责。

## 十分钟开始

准备 Python **3.11**，从 GitHub 下载或克隆本仓库，进入包含本文件的目录。真实请求可能收费，需要自行准备兼容 OpenAI Chat Completions 的服务配置。供应商提供的模型名、地址、密钥应来自同一套服务；不要假定任何模型一定免费或支持工具调用。

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

如果系统没有 `py`，确认 `python --version` 是 3.11 后使用 `python -m venv .venv`。激活受限时可直接使用 `.\.venv\Scripts\python.exe` 代替后续命令中的 `python`，无需修改系统执行策略。

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

打开 `.env`，填写以下三个值；不要把密钥提交到 GitHub：

```dotenv
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-provider.example/v1
LLM_MODEL=your-model-name
```

配置检查与第一条真实请求：

```console
python -m scripts.check_config
python -m learning.steps_01_20.step_01_basic_chat
```

预期获得一句关于 API 的解释。文字可以不同；这个步骤默认 30 秒超时、不自动重试。401/403 检查权限，429 停止并等待额度恢复，连接失败检查地址和网络。完整说明见 [安装与排错](docs/setup.md)。

启动正式接口：

```console
python -m uvicorn main:app --reload
```

打开 <http://127.0.0.1:8000/docs>。向 `POST /api/chat/conversation` 提交：

```json
{"conversation_id":"demo-1","message":"请查询订单10001的物流单号。"}
```

模型需要支持工具调用。订单查询使用仓库内的**虚构演示数据**，不连接电商平台；回答应由工具结果支持。同一会话继续问“它的状态呢？”可观察记忆。结束服务按 Ctrl+C。

## 学习顺序

| 阶段 | 核心内容 | 阅读入口 |
| --- | --- | --- |
| 1. Python/FastAPI 与原生 Agent | 输入校验、工具调用、测试、多轮记忆 | [基础 1～20](learning/steps_01_20/README.md) |
| 2. 基础 RAG | 文档、chunk、n-gram、Prompt、拒答、来源、知识工具 | [RAG 1～14B](learning/rag/README.md) |
| 3. 向量检索与评测 | Embedding、缓存、Dense、RRF、阈值与留出验证 | [从 15A 开始](learning/rag/step_15a_keyword_limit.md) |
| 4. 上下文工程 | 历史、事实、摘要实验、压缩、信任边界 | [18A～18M](learning/context/README.md) |
| 5. LangChain / LangGraph | 工具对象、运行器、状态图、Checkpoint、HTTP 适配 | [19A～20M](learning/frameworks/README.md) |

新增进阶内容（保留原步骤编号）：

| 单元 | 主要成果 | 入口 |
| --- | --- | --- |
| Web基础补充 | 参数、异步、Depends、lifespan、进程与错误 | [9课](learning/web_basics/README.md) |
| MCP | stdio/HTTP、工具格式适配、错误分层、模型循环 | [21A～21H](learning/mcp/README.md) |
| 效果评测 | 正式HTTP轨迹、required/optional/none、证据与留出题 | [11课](learning/evaluation/README.md) |
| Docker | 镜像、容器、端口、数据卷与Compose | [3课](learning/docker/README.md) |
| PostgreSQL | Python参数化查询与正式订单工具 | [5课](learning/postgresql/README.md) |
| pgvector | 入库、余弦检索、完整章节、事务更新与正式接入 | [12课](learning/pgvector/README.md) |

入门默认无数据库：`ORDER_STORAGE_BACKEND=demo`、`KNOWLEDGE_RETRIEVAL_BACKEND=ngram`。进入数据库章节后按 [安装顺序](docs/database.md)创建独立教学库，再明确切换后端。不要把维护者本机已经启用的配置当作新读者的初始环境。

[完整课程目录](learning/README.md) · [阶段复盘](docs/recap.md) · [调用链图](docs/architecture.md) · [面试速查](learning/INTERVIEW_QUICK_REFERENCE.md)

每课先看前置知识和“访问范围”，再运行。检查题先独立回答，再展开答案。课程中的脚本是分步练习，`app` 是最终整合版；前几课不要求一次读懂全部 `app`。

## 能力与边界

| 部分 | 当前实现 | 不应误解为 |
| --- | --- | --- |
| 正式 Agent | 原生三工具循环；订单默认demo，可切PostgreSQL | 真实电商接入、退款写操作 |
| 正式 RAG | 默认n-gram；可配置pgvector，两个入口共用检索；返回sources | 所有读者已建库或已完成大规模质量校准 |
| 向量检索 | V4/1536持久化、问题余弦Top-K；Dense/Hybrid独立实验 | 不同模型可混用向量、召回即证据充分 |
| 会话 | 进程内历史、十轮窗口、订单号和有限退款偏好 | 数据库持久化、通用语义记忆、Token 预算控制 |
| 上下文实验 | 人工摘要、字段压缩、消息结构与指标演示 | 自动摘要和生产监控已上线 |
| LangGraph | 独立状态图与工具循环，20M 用模拟模型演示 HTTP 双工具 | 正式接口已迁移图服务、已实现审批界面 |

流式入口演示文本输出，不代表实现了流式工具循环。订单偏好只保存数据，不执行退款。相关文档检索到不代表答案存在；引用来源也不自动证明每个断言正确。

## 目录与验证

```text
app/                 正式API、服务、工具和检索组件
data/knowledge/      三篇示例知识文档
learning/            分阶段讲义、实验和参考答案
tests/               正式模块与检索组件的本地检查
scripts/             配置、离线验证、真实烟测和文档检查
docs/                安装、架构、复盘、贡献发布相关说明
```

无需真实密钥的检查（主动覆盖配置为假值，并阻止外部连接）：

```console
python -m scripts.check_docs
python -m scripts.verify_offline --suite base
```

框架阶段使用单独环境，安装及验证命令见 [安装说明](docs/setup.md)。[验证记录](docs/validation.md)区分本机结果、真实服务结果与尚未运行的平台检查。

新增MCP环境使用 `learning/mcp/requirements.txt`；可运行 `python -m scripts.verify_offline --suite mcp` 验证stdio与本机HTTP，不调用模型。效果评测默认只预览，显式 `--run` 才使用真实模型；数据库与Embedding写入不在默认CI中执行。

## 常见问题

- **需要先装 LangChain 吗？** 不需要；进入第五阶段再创建框架环境。
- **为什么运行脚本要用 `-m`？** 从仓库根目录运行模块，保证 `app` 和 `learning` 的导入路径一致。
- **如何看不到模型请求也能验证链路？** 测试替换模型响应，但仍执行本地路由、工具与状态处理；这只能证明对应程序逻辑。
- **如何继续完善项目？** 先学习新增的MCP、评测和数据库章节，再按需求扩展会话持久化与部署。订单和向量已可持久化，会话仍在进程内。

欢迎按 [贡献指南](CONTRIBUTING.md)提交修正。代码和教程采用 [MIT 许可](LICENSE)。发布自己的副本前，请看 [GitHub 上传说明](docs/publishing.md)。
