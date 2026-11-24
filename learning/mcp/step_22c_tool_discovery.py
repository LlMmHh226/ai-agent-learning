"""22C：本机发现、工具说明转换、允许范围校验与只读调用。"""

import asyncio
import json
from typing import Literal

from mcp import Client

from learning.mcp.step_21c_tool_adapter import execute_model_call, to_model_tools
from learning.mcp.step_22b_order_lifecycle import ORDER_TOOL, connect_order_server


SCOPES = {
    "orders": (ORDER_TOOL,),
    "all": (ORDER_TOOL, "get_after_sales_policy", "search_knowledge_base"),
}


async def discover(client: Client, scope: Literal["orders", "all"]) -> list[dict]:
    expected = SCOPES[scope]
    listed = (await client.list_tools()).tools
    by_name = {tool.name: tool for tool in listed}
    if len(by_name) != len(listed):
        raise ValueError("发现结果包含重复工具名")
    missing = set(expected) - by_name.keys()
    if missing:
        raise ValueError("未发现所需的教学工具")
    return to_model_tools([by_name[name] for name in expected])


def names(definitions: list[dict]) -> set[str]:
    return {item["function"]["name"] for item in definitions}


async def main() -> None:
    async with connect_order_server() as client:
        orders = await discover(client, "orders")
        all_tools = await discover(client, "all")
        assert names(orders) == set(SCOPES["orders"])
        assert names(all_tools) == set(SCOPES["all"])
        print("orders:", sorted(names(orders)))
        print("all:", sorted(names(all_tools)))
        policy_call = {
            "id": "demo-policy", "type": "function",
            "function": {"name": "get_after_sales_policy", "arguments": '{"topic":"退货"}'},
        }
        try:
            await execute_model_call(client, policy_call, names(orders))
        except ValueError:
            print("orders 范围拒绝调用售后工具，未向服务端发这次请求。")
        else:
            raise AssertionError("服务端存在的工具不代表 Host 已授权使用")
        policy_result = await execute_model_call(client, policy_call, names(all_tools))
        assert policy_result["tool_call_id"] == "demo-policy"
        assert json.loads(policy_result["content"])["topic"] == "退货"
        print("all 范围的固定样例调用：", policy_result)


if __name__ == "__main__":
    asyncio.run(main())
