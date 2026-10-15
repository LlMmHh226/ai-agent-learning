# 安装、模型配置与排错

[返回首页](../README.md)

## 环境约定

首版验证基线为 Python 3.11；所有课程从仓库根目录运行，使用 `python -m 模块名`。基础与框架使用两个独立虚拟环境，不使用 `--system-site-packages`。

基础环境按首页安装。`requirements.in` 记录直接依赖范围，`requirements.txt` 是解析后的完整固定版本清单。框架清单包含完整应用依赖，不能假设另一个环境中的包会自动可用。普通读者安装 `.txt` 即可。

## 真实模型配置

复制 `.env.example` 为 `.env`，填写 Key、服务地址、模型名称；默认使用 Chat Completions 兼容接口。部分服务的地址需包含 `/v1`，以供应商文档为准，不要把网页聊天地址填入 API 配置。

先运行 `python -m scripts.check_config`，再运行第一课。配置检查只确认必填项，不发送网络请求。第一课成功后才进入工具调用；工具模型还需要支持 `tools`、`tool_choice` 和工具消息返回。

如需单独检查真实链路：

```console
python -m scripts.smoke_real
```

最多三次模型请求：一句问候、订单工具选择、工具结果后的最终回答。不自动重试；任一步失败停止。看到 `CHAT_OK` 只证明基础聊天；看到 `TOOL_ROUNDTRIP_OK` 才说明该次订单往返成功，不代表所有题目效果已验证。

## 框架环境

退出当前环境后，在仓库根目录创建独立环境。

Windows PowerShell：

```powershell
deactivate
py -3.11 -m venv .venv-langchain
.\.venv-langchain\Scripts\Activate.ps1
python -m pip install -r learning/frameworks/requirements.txt
python -m scripts.verify_offline --suite framework
```

macOS/Linux：

```bash
deactivate
python3.11 -m venv .venv-langchain
source .venv-langchain/bin/activate
python -m pip install -r learning/frameworks/requirements.txt
python -m scripts.verify_offline --suite framework
```

`deactivate` 仅在已经激活虚拟环境时使用。框架测试模拟模型；课程 19B、19C、19E、19F 和 20I 的直接运行入口访问真实模型，19D、20A～20H、20J～20M 是本地演示，先阅读各课标注。

## Embedding 配置

进入 RAG 16B 时才在 `.env` 增加：

```dotenv
DASHSCOPE_API_KEY=your-dashscope-api-key
EMBEDDING_PROVIDER=dashscope
EMBEDDING_MODEL=text-embedding-v2
EMBEDDING_DIMENSIONS=1536
```

本项目实际使用 DashScope SDK，而不是 LlamaIndex。聊天 Key 与百炼 Key 可以属于不同服务。模型权限、额度、价格由供应商决定；教程不保证免费额度。`1536` 用于检查 v2 返回向量长度，不是截取前 1536 维或改变模型结构。

知识库和测试问题会在真实向量实验中发送给服务商。当前是虚构样例；替换为自己的资料后应确认资料可以外发。不要一口气执行全部真实评测脚本。

## 离线验证

```console
python -m scripts.verify_offline --suite base
python -m scripts.check_docs
```

离线入口覆盖 `.env` 中的配置为假值，关闭追踪上传并阻止外部 socket 连接。Windows asyncio 内部使用的本机 socketpair 是事件循环机制，不是模型请求。不要用递归发现所有 `learning` 文件的方式替代这个白名单入口，否则可能运行真实模型实验。

## 常见故障

| 现象 | 先检查什么 |
| --- | --- |
| `No module named app` | 是否在仓库根目录，是否使用 `python -m` |
| 缺少 `langchain` / `langgraph` | 是否激活框架环境并安装其完整依赖 |
| 配置校验失败 | `.env` 是否放在仓库根目录，三个聊天字段是否填写 |
| 401 / 403 | Key 是否属于该服务、模型是否授权；不要输出 Key |
| 404 | API 基础地址和模型名称，兼容接口路径是否正确 |
| 429 | 限流或额度不足；停止实验，等待或核实额度，不循环重试 |
| 连接超时 | 网络、代理和服务地址；不要为修复连接而改工具逻辑 |
| 普通聊天成功，工具课失败 | 该模型是否支持工具调用，返回的工具名称与参数是否符合协议 |
| 中文乱码 | 使用 UTF-8 终端，必要时 `python -X utf8 -m ...` |
| 重启后会话消失 | 当前会话和内存 Checkpoint 都是进程内数据，这是实现边界 |

报告问题时提供 Python 版本、课程编号、异常类型和脱敏后的状态码。不要提交 `.env`、完整请求头或供应商错误中的敏感字段。
