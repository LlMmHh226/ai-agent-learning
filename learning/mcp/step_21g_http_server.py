# 课程：step_21g_http_transport.md；访问范围：本地演示，不请求外部模型。
"""21G：复用已注册的订单工具，通过本机Streamable HTTP提供MCP服务。"""

from learning.mcp.step_21b_order_server import server
import os


if __name__ == "__main__":
    # 导入21B只取得server及工具注册，不执行它的__main__里的stdio启动。
    # 仅监听本机；本演示不暴露公网，也未实现生产身份鉴权。
    server.run(transport="streamable-http", host="127.0.0.1", port=int(os.environ.get("MCP_HTTP_PORT", "8765")))
