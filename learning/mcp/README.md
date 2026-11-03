# MCP工具连接

[课程总目录](../README.md)

先学习角色与stdio，再适配模型工具格式、区分错误、构造循环，最后比较真实模型、HTTP与生命周期。MCP传输真实并不等于模型响应真实。

服务端使用独立的虚构订单函数，不读取聊天密钥或数据库配置。stdio子进程的环境由SDK管理，不能假定它会继承Host的所有变量；模型密钥只由真实模型客户端使用。正式应用的PostgreSQL模式在数据库章节另行启用。

- [21A MCP中的角色](step_21a_mcp_roles.md) — 本地演示，不请求外部模型
- [21B stdio订单服务](step_21b_local_order.md) — 本地演示，不请求外部模型
- [21C 模型格式适配](step_21c_tool_adapter.md) — 本地演示，不请求外部模型
- [21D MCP错误分层](step_21d_error_layers.md) — 本地演示，不请求外部模型
- [21E MCP工具循环](step_21e_mcp_tool_loop.md) — 本地演示，不请求外部模型
- [21F 真实模型与MCP](step_21f_real_model_mcp.md) — 真实外部模型请求，可能收费
- [21G Streamable HTTP](step_21g_http_transport.md) — 本地演示，不请求外部模型
- [21H FastAPI复用MCP连接](step_21h_fastapi_lifespan.md) — 本地演示，不请求外部模型
