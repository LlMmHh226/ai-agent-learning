# 21G · Streamable HTTP

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

比较stdio与HTTP连接。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [真实模型与MCP](step_21f_real_model_mcp.md)。 使用环境：.venv-mcp。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [step_21g_http_client.py](step_21g_http_client.py)：本课学习代码。
- [step_21g_http_server.py](step_21g_http_server.py)：本课学习代码。
- [独立依赖](requirements.txt)：使用MCP环境安装，不混入框架环境。

## 具体输入与执行过程

```text
先独立启动Server
→ Client按URL连接
→ 发现/查询
→ 客户端退出
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：本地演示，不请求外部模型。**

```console
python -m learning.mcp.step_21g_http_client
```

应观察到：仅本机8765端口，Server由启动方单独关闭。



先在第二个终端、同一MCP环境运行 `python -m learning.mcp.step_21g_http_server`；保持运行，再执行上面的客户端。结束时在服务端终端按Ctrl+C。默认地址为本机8765端口，环境变量MCP_HTTP_PORT可更改端口。

## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 不会；HTTP Server通常独立运行，与stdio由客户端启动子进程的生命周期不同。

## 自测与参考答案

1. HTTP客户端退出后一定杀掉Server吗？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 不会；HTTP Server通常独立运行，与stdio由客户端启动子进程的生命周期不同。
2. 先独立启动Server → Client按URL连接 → 发现/查询 → 客户端退出。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“比较stdio与HTTP连接”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
