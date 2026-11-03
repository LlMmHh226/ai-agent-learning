# 课程：step_21b_local_order.md；访问范围：本地演示，不请求外部模型。
"""21B：启动独立服务端、发现工具、发起真实本地MCP调用。"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def main() -> None:
    """无参数客户端入口；通过标准输入输出连接子进程，展示查询结果。"""
    project_root = Path(__file__).resolve().parents[2]
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.step_21b_order_server"],
        cwd=str(project_root),
    )
    # 进入上下文时SDK启动服务端子进程并建立MCP连接；退出时负责关闭。
    async with Client(server_parameters, read_timeout_seconds=15) as client:
        listing = await client.list_tools()
        print("服务端提供的工具：", [item.name for item in listing.tools])
        order_tool = next(item for item in listing.tools if item.name == "query_order")
        print("工具参数说明：", order_tool.input_schema)

        result = await client.call_tool("query_order", {"order_id": "10001"})
        print("调用结果类型：", type(result).__name__)
        print("协议结果：", result.model_dump_json(by_alias=True, exclude_none=True))
        assert not result.is_error
        data = result.structured_content
        assert isinstance(data, dict)
        assert data["found"] is True
        assert data["order_id"] == "10001"
        assert data["tracking_number"] == "SF1234567890"
        print("取出业务结果：", json.dumps(data, ensure_ascii=False))
    print("MCP连接已关闭，服务端子进程已退出；没有调用大模型。")


if __name__ == "__main__":
    asyncio.run(main())
