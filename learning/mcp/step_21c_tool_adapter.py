# 课程：step_21c_tool_adapter.md；访问范围：本地演示，不请求外部模型。
"""21C：适配工具说明与调用参数；手写Tool Call，真实本地MCP通信。"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.types import Tool


def to_model_tools(tools: list[Tool]) -> list[dict]:
    """tools来自listing.tools；返回OpenAI兼容Chat Completions工具定义列表。

    本例MCP输入Schema可直接复用，不声称所有供应商/strict模式都兼容。
    """
    return [
        {"type": "function", "function": {
            "name": item.name,
            "description": item.description or "",
            "parameters": item.input_schema,
        }}
        for item in tools
    ]


async def execute_model_call(client: Client, tool_call: dict, known_names: set[str]) -> dict[str, str]:
    """接收模型样式的调用dict，解析参数，经MCP执行后返回模型tool消息。

    client是已连接的MCP客户端；tool_call由main手写模拟，实际项目可从模型响应转换。
    known_names来自服务端工具列表，用于拒绝未登记名称。返回消息交回main列表。
    """
    call_id = tool_call["id"]
    name = tool_call["function"]["name"]
    if not isinstance(call_id, str) or not call_id:
        raise ValueError("工具调用ID必须是非空字符串。")
    if name not in known_names:
        raise ValueError("模型请求了未登记的工具。")
    arguments = json.loads(tool_call["function"]["arguments"])
    if not isinstance(arguments, dict):
        raise ValueError("工具参数必须解析为字典。")

    result = await client.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError("MCP工具执行失败；本步停止，不生成成功结果。")
    # 本服务端返回结构化订单dict；其他工具也可能只返回content内容块。
    payload = result.structured_content
    if payload is None:
        payload = [item.model_dump(by_alias=True, exclude_none=True) for item in result.content]
    return {
        "role": "tool",
        "tool_call_id": call_id,
        "content": json.dumps(payload, ensure_ascii=False),
    }


async def main() -> None:
    """无参数入口：发现工具、转换说明、执行手写调用，展示可交给模型的消息。"""
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.step_21b_order_server"],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    async with Client(server_parameters, read_timeout_seconds=15) as client:
        listing = await client.list_tools()
        model_tools = to_model_tools(listing.tools)
        print("可提供给Chat Completions的工具定义：")
        print(json.dumps(model_tools, ensure_ascii=False, indent=2))
        assert model_tools[0]["function"]["parameters"] == listing.tools[0].input_schema

        # 这是手写样例，不是本轮模型实际生成的调用。
        tool_call = {
            "id": "call_order_demo", "type": "function",
            "function": {"name": "query_order", "arguments": '{"order_id": "10001"}'},
        }
        known_names = {item.name for item in listing.tools}
        tool_message = await execute_model_call(client, tool_call, known_names)
        assert tool_message["tool_call_id"] == "call_order_demo"
        assert json.loads(tool_message["content"])["tracking_number"] == "SF1234567890"

        messages = [
            {"role": "system", "content": "查询订单时使用工具，根据结果回答。"},
            {"role": "user", "content": "查询订单10001的物流单号。"},
            {"role": "assistant", "content": None, "tool_calls": [tool_call]},
            tool_message,
        ]
        print("已组装但尚未发给模型的消息：")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        print("检查通过：JSON参数→MCP调用→tool结果；没有真实模型请求。")


if __name__ == "__main__":
    asyncio.run(main())
