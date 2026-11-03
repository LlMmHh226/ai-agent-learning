# 课程：step_21d_error_layers.md；访问范围：本地演示，不请求外部模型。
"""21D：观察MCP正常结果、业务未找到、参数错误和未知工具，不调用模型。"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, MCPError, StdioServerParameters


async def inspect_call(client: Client, name: str, arguments: dict) -> dict:
    """main提供连接、工具名和参数；返回错误层级与数据供main核对。

    MCPError表示本次收到协议错误；is_error表示返回了工具错误结果。
    found是业务数据中的字段，不是MCP标准成功标志。
    """
    try:
        result = await client.call_tool(name, arguments)
    except MCPError as error:
        return {"layer": "protocol_error", "code": error.code, "message": error.message}

    if result.is_error:
        return {
            "layer": "tool_error", "is_error": True,
            "messages": [item.text for item in result.content if item.type == "text"],
        }
    return {"layer": "normal_result", "is_error": False, "data": result.structured_content}


async def main() -> None:
    """无参数，真实调用本地21B服务端，打印每种情况的实际返回形态。"""
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.step_21b_order_server"],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    cases = [
        ("存在的订单", "query_order", {"order_id": "10001"}),
        ("不存在的订单", "query_order", {"order_id": "99999"}),
        ("缺少必填参数", "query_order", {}),
        ("未注册工具名", "query_order_typo", {"order_id": "10001"}),
    ]
    observations = []
    async with Client(parameters, read_timeout_seconds=15) as client:
        listing = await client.list_tools()
        assert "query_order" in {item.name for item in listing.tools}
        for label, name, arguments in cases:
            # 故意不经过21C的known_names检查，观察服务端/协议自己的错误响应。
            observation = await inspect_call(client, name, arguments)
            observations.append(observation)
            print(label, "：", json.dumps(observation, ensure_ascii=False))
    assert observations[0]["layer"] == "normal_result"
    assert observations[0]["data"]["found"] is True
    assert observations[1]["layer"] == "normal_result"
    assert observations[1]["data"]["found"] is False
    assert observations[2]["layer"] in ("tool_error", "protocol_error")
    assert observations[3]["layer"] in ("tool_error", "protocol_error")
    print("检查通过：业务未找到不等于MCP调用出错；原服务端及业务代码未改。")


if __name__ == "__main__":
    asyncio.run(main())
