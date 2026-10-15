# 课程：step_20j_native_graph_comparison.md；访问范围：本地运行（无外部模型请求）。
"""20J：真实原生工具循环与图循环对照；仅模型响应模拟，无网络请求。"""

import asyncio
import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from openai.types.chat import ChatCompletionMessage

import app.services.llm_service as native
from learning.frameworks import step_19d_langchain_tool_object as tool_module
from learning.frameworks.step_20i_tool_loop_graph import build_graph, initial_input


def simulated_answer(result: dict) -> str:
    """result来自实际执行的本地订单工具；返回两条路线共用的模拟正文。"""
    if not result["found"]:
        return "模拟回答：没有找到该订单。"
    return "模拟回答：物流单号为" + str(result["tracking_number"] or "暂无") + "。"


async def run_native(order_id: str) -> dict:
    """main传入订单号；运行正式LLMService循环，返回计数/消息/结果供对照。"""
    messages = [{"role": "system", "content": native.DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": f"请查询订单{order_id}的物流单号。"}]
    original = deepcopy(messages)
    sent_messages = []

    async def fake_create(**kwargs):
        """正式SDK调用参数进入kwargs；返回形状匹配的本地模拟响应。"""
        sent_messages.append(deepcopy(kwargs["messages"]))
        if len(sent_messages) == 1:
            message = ChatCompletionMessage(role="assistant", content=None, tool_calls=[{
                "id": "call_native", "type": "function",
                "function": {"name": "get_order_status", "arguments": json.dumps({"order_id": order_id})},
            }])
        else:
            tool_message = kwargs["messages"][-1]
            assert tool_message["role"] == "tool"
            assert tool_message["tool_call_id"] == "call_native"
            message = ChatCompletionMessage(role="assistant", content=simulated_answer(json.loads(tool_message["content"])))
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    # 只替换底层模型响应；正式_execute_tool和订单函数实际执行。
    with patch.object(native.llm_service.client.chat.completions, "create", side_effect=fake_create), patch.object(native, "get_order_status", wraps=native.get_order_status) as lookup:
        answer = await native.llm_service.chat_with_messages(messages)
        assert lookup.call_count == 1
        lookup.assert_called_with(order_id)
    assert messages == original
    return {"answer": answer, "model_calls": len(sent_messages), "tool_calls": lookup.call_count,
            "input_lengths": [len(items) for items in sent_messages],
            "second_roles": [item["role"] for item in sent_messages[1]],
            "return_type": type(answer).__name__}


async def run_graph(order_id: str) -> dict:
    """main传入同一个订单号；实际运行20I图，返回与原生可对照的观测值。"""
    sent_messages = []
    async def fake_generate(model, messages, *args, **kwargs):
        """图调用模型时传入messages；模拟Tool Call，再按真实工具结果生成正文。"""
        sent_messages.append(list(messages))
        if len(sent_messages) == 1:
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_order", "args": {"order_id": order_id}, "id": "call_graph",
            }])
        else:
            assert isinstance(messages[-1], ToolMessage)
            assert messages[-1].tool_call_id == "call_graph"
            reply = AIMessage(content=simulated_answer(json.loads(messages[-1].content)))
        return ChatResult(generations=[ChatGeneration(message=reply)])

    with patch.object(ChatOpenAI, "_agenerate", new=fake_generate), patch.object(tool_module, "get_order_status", wraps=tool_module.get_order_status) as lookup:
        model = ChatOpenAI(model="local-test", api_key="test-only", base_url="https://example.invalid")
        graph = build_graph(model)
        result = await graph.ainvoke(initial_input(f"请查询订单{order_id}的物流单号。"), config={"recursion_limit": 6})
        lookup.assert_called_once_with(order_id)
    roles = {"system": "system", "human": "user", "ai": "assistant", "tool": "tool"}
    return {"answer": result["messages"][-1].content,
            "model_calls": len(sent_messages), "tool_calls": lookup.call_count,
            "input_lengths": [len(items) for items in sent_messages],
            "second_roles": [roles[item.type] for item in sent_messages[1]],
            "return_type": type(result).__name__, "final_message_count": len(result["messages"])}


async def main() -> None:
    """无参数；用找到/没找到两个订单对照两路线，不评估模型语义或性能。"""
    for order_id in ("10001", "99999"):
        native_result = await run_native(order_id)
        graph_result = await run_graph(order_id)
        for field in ("answer", "model_calls", "tool_calls", "input_lengths", "second_roles"):
            assert native_result[field] == graph_result[field], field
        assert native_result["input_lengths"] == [2, 4]
        assert graph_result["final_message_count"] == 5
        print("订单：", order_id)
        print("原生：", native_result)
        print("图版：", graph_result)
    print("对照通过：两路线均实际执行本地工具，模型响应均模拟。")


if __name__ == "__main__":
    asyncio.run(main())
