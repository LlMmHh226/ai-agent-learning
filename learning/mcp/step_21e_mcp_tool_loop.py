# 课程：step_21e_mcp_tool_loop.md；访问范围：本地演示，不请求外部模型。
"""21E：真实MCP工具循环，模型用显式模拟函数；不使用patch或外部模型。"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, MCPError, StdioServerParameters

from learning.mcp.step_21c_tool_adapter import to_model_tools


async def execute_mcp_call(client: Client, tool_call: dict, known_names: set[str]) -> dict:
    """loop传入客户端、Tool Call和工具名集合；返回关联ID的tool消息。

    content包含ok/data或ok/error。业务found=False仍属于ok=True。
    本例只处理格式正确的Tool Call外壳；参数JSON错误、未知工具、服务端工具错误
    和MCP协议错误转换为失败结果。连接断开等未处理异常仍向调用方抛出。
    """
    name = tool_call["function"]["name"]
    if name not in known_names:
        payload = {"ok": False, "error": "unknown_tool", "message": "该工具未注册。"}
    else:
        try:
            arguments = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            payload = {"ok": False, "error": "invalid_json", "message": "参数不是有效JSON。"}
        else:
            if not isinstance(arguments, dict):
                payload = {"ok": False, "error": "invalid_arguments", "message": "参数必须为对象。"}
            else:
                try:
                    result = await client.call_tool(name, arguments)
                except MCPError as error:
                    payload = {"ok": False, "error": "protocol_error", "code": error.code}
                else:
                    if result.is_error:
                        # 本地只读样例的诊断文字供模拟模型修参数；生产需过滤敏感详情。
                        payload = {"ok": False, "error": "tool_error", "message": "\n".join(
                            item.text for item in result.content if item.type == "text"
                        )}
                    else:
                        data = result.structured_content
                        if data is None:
                            data = [item.model_dump(by_alias=True, exclude_none=True) for item in result.content]
                        payload = {"ok": True, "data": data}
    print("工具结果：", json.dumps(payload, ensure_ascii=False))
    return {
        "role": "tool", "tool_call_id": tool_call["id"],
        "content": json.dumps(payload, ensure_ascii=False),
    }


async def run_tool_loop(client: Client, ask_model, messages: list[dict], max_model_calls: int = 3) -> str:
    """main提供已连接client、异步模型函数、初始消息和调用上限；返回最终正文。

    ask_model接收(messages, model_tools)，返回含content/tool_calls的assistant字典。
    21E传入simulate_model；21F可传入真实SDK适配函数。此签名是本应用约定。
    """
    listing = await client.list_tools()
    model_tools = to_model_tools(listing.tools)
    known_names = {item.name for item in listing.tools}
    working_messages = [dict(message) for message in messages]
    for round_index in range(max_model_calls):
        print(f"第{round_index + 1}次调用模型函数，消息{len(working_messages)}条。")
        reply = await ask_model(working_messages, model_tools)
        if not reply.get("tool_calls"):
            answer = reply.get("content")
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("模型没有返回非空回答。")
            return answer
        # 最后一轮还要求工具时停止，不执行已无法交回模型处理的新工具请求。
        if round_index == max_model_calls - 1:
            return "工具流程达到调用上限，暂时无法完成。"
        working_messages.append(reply)
        for tool_call in reply["tool_calls"]:
            tool_message = await execute_mcp_call(client, tool_call, known_names)
            working_messages.append(tool_message)
    raise ValueError("max_model_calls必须为正数。")


def make_simulated_model(order_id: str, omit_first_argument: bool = False):
    """main提供教学订单号和是否首次漏参；返回模拟模型函数与观察列表。

    模型选择和纠错均为手写规则，不声称真实模型会自动修复。
    """
    observations = []

    async def simulate_model(messages: list[dict], model_tools: list[dict]) -> dict:
        """loop传入消息和说明；返回一条模拟assistant消息。"""
        assert any(item["function"]["name"] == "query_order" for item in model_tools)
        observations.append(len(messages))
        if messages[-1]["role"] == "tool":
            payload = json.loads(messages[-1]["content"])
            if payload["ok"]:
                data = payload["data"]
                answer = ("模拟回答：物流单号为" + data["tracking_number"] + "。"
                          if data["found"] else "模拟回答：没有找到订单，请核对订单号。")
                return {"role": "assistant", "content": answer}
            print("模拟模型读取错误，准备补齐order_id再次调用。")
        arguments = {} if omit_first_argument and len(observations) == 1 else {"order_id": order_id}
        return {"role": "assistant", "content": None, "tool_calls": [{
            "id": f"call_{len(observations)}", "type": "function",
            "function": {"name": "query_order", "arguments": json.dumps(arguments)},
        }]}
    return simulate_model, observations


async def main() -> None:
    """无参数，运行成功/业务未找到/漏参后修正三例，以及上限检查。"""
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.step_21b_order_server"],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    async with Client(parameters, read_timeout_seconds=15) as client:
        for order_id, omit in (("10001", False), ("99999", False), ("10001", True)):
            simulate_model, observed = make_simulated_model(order_id, omit)
            messages = [
                {"role": "system", "content": "用工具查订单；失败不等于订单不存在，不猜测缺失参数。"},
                {"role": "user", "content": f"查询订单{order_id}的物流单号。"},
            ]
            answer = await run_tool_loop(client, simulate_model, messages)
            assert observed == ([2, 4, 6] if omit else [2, 4])
            assert len(messages) == 2
            assert ("没有找到" if order_id == "99999" else "SF1234567890") in answer
            print("最终：", answer, "\n")

        # 不调用工具：唯一一次模型响应仍要求工具，循环直接按上限停止。
        simulate_model, observed = make_simulated_model("10001")
        answer = await run_tool_loop(client, simulate_model, [
            {"role": "user", "content": "查询10001"},
        ], max_model_calls=1)
        assert "达到调用上限" in answer and observed == [1]
        print("上限检查：", answer)
    print("本地MCP循环检查通过；模型响应均为显式模拟。")


if __name__ == "__main__":
    asyncio.run(main())
