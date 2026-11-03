# 课程：step_21g_http_transport.md；访问范围：本地演示，不请求外部模型。
"""21G：连接已经独立运行的HTTP MCP服务端，不启动服务端子进程。"""

import asyncio
import json
import os

from mcp import Client


SERVER_URL = "http://127.0.0.1:" + os.environ.get("MCP_HTTP_PORT", "8765") + "/mcp"


async def main() -> None:
    """无参数；通过URL连接MCP Server，列出工具并调用订单查询。"""
    async with Client(SERVER_URL, read_timeout_seconds=15) as client:
        listing = await client.list_tools()
        print("HTTP MCP工具：", [item.name for item in listing.tools])
        assert "query_order" in {item.name for item in listing.tools}
        result = await client.call_tool("query_order", {"order_id": "10001"})
        assert not result.is_error
        data = result.structured_content
        assert isinstance(data, dict)
        assert data["tracking_number"] == "SF1234567890"
        print("HTTP MCP查询结果：", json.dumps(data, ensure_ascii=False))
    print("客户端连接已关闭；独立服务端由其启动方负责停止。")


if __name__ == "__main__":
    asyncio.run(main())
