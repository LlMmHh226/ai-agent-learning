# 21H · FastAPI复用MCP连接

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

在lifespan中管理连接。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [Streamable HTTP](step_21g_http_transport.md)。 使用环境：.venv-mcp。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [step_21h_fastapi_lifespan.py](step_21h_fastapi_lifespan.py)：本课学习代码。
- [独立依赖](requirements.txt)：使用MCP环境安装，不混入框架环境。

## 具体输入与执行过程

```text
启动建立Client
→ app.state保存
→ 多个HTTP请求复用
→ 关闭清理
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：本地演示，不请求外部模型。**

```console
python -m learning.mcp.step_21h_fastapi_lifespan
```

应观察到：进程内HTTP与真实stdio进程运行，无模型调用。



需要先理解Web补充课的Depends、lifespan和app.state。本课Client只在当前进程复用，不实现跨worker共享连接或持久化记忆。

## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 不是；它是应用进程的基础设施连接，会话数据由会话服务另行管理。

## 自测与参考答案

1. 共享MCP连接是保存用户聊天历史吗？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 不是；它是应用进程的基础设施连接，会话数据由会话服务另行管理。
2. 启动建立Client → app.state保存 → 多个HTTP请求复用 → 关闭清理。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“在lifespan中管理连接”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
