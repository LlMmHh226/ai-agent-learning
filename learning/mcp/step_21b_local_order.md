# 21B · stdio订单服务

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

发现并调用独立进程中的工具。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [MCP中的角色](step_21a_mcp_roles.md)。 使用环境：.venv-mcp。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [step_21b_order_client.py](step_21b_order_client.py)：本课学习代码。
- [step_21b_order_server.py](step_21b_order_server.py)：本课学习代码。
- [独立依赖](requirements.txt)：使用MCP环境安装，不混入框架环境。

## 具体输入与执行过程

```text
Client启动子进程
→ list_tools
→ call_tool(query_order,10001)
→ structured_content
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：本地演示，不请求外部模型。**

```console
python -m learning.mcp.step_21b_order_client
```

应观察到：真实本地MCP通信返回订单，不访问模型。





## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- stdio传输使用stdout承载协议，普通日志可能破坏消息格式；日志应走stderr。

## 自测与参考答案

1. 为何Server不能随便print到stdout？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. stdio传输使用stdout承载协议，普通日志可能破坏消息格式；日志应走stderr。
2. Client启动子进程 → list_tools → call_tool(query_order,10001) → structured_content。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“发现并调用独立进程中的工具”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
