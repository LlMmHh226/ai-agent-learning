# 课程：step_20m_knowledge_tool.md；访问范围：本地运行（无外部模型请求）。
"""20M：同一图提供订单/知识库工具，进程内HTTP演示，模型模拟。"""

import asyncio
import json
from unittest.mock import patch

import httpx
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from main import app
import app.api.chat as chat_api
from app.services.conversation_service import ConversationService, llm_service
from app.tools.knowledge_tools import search_knowledge_base
from learning.frameworks.step_19d_langchain_tool_object import lookup_order
from learning.frameworks.step_20i_tool_loop_graph import build_graph
from learning.frameworks.step_20k_graph_conversation import make_graph_chat


@tool
def search_faq(query: str) -> dict[str, object]:
    """搜索本地商品说明等知识资料，返回片段和来源；不用于查询实时订单。

    Args:
        query: 用户要检索的完整问题字符串，由工具调用参数提供。
    """
    return search_knowledge_base(query)


async def main() -> None:
    """无参数，本地验证订单、商品资料、无资料三条HTTP调用链。"""
    cases = [
        ("请查询订单10001的物流单号。", "lookup_order", {"order_id": "10001"}),
        ("星云机械键盘支持热插拔吗？", "search_faq", {"query": "星云机械键盘支持热插拔吗？"}),
        ("商品有优惠券吗？", "search_faq", {"query": "商品有优惠券吗？"}),
    ]
    by_question = {question: (name, arguments) for question, name, arguments in cases}
    calls = []
    results = []

    async def fake_generate(model, messages, *args, **kwargs):
        """按固定题目模拟工具选择；工具结果实际检索，不评价模型语义能力。"""
        assert {item["function"]["name"] for item in kwargs["tools"]} == {"lookup_order", "search_faq"}
        if isinstance(messages[-1], ToolMessage):
            data = json.loads(messages[-1].content)
            results.append(data)
            if not data["found"]:
                answer = "模拟回答：根据现有知识库资料，我无法确认。"
            elif "tracking_number" in data:
                answer = "模拟回答：物流单号为" + data["tracking_number"] + "。"
            else:
                hit = data["results"][0]
                # 从真实命中片段提取原句；不硬编码知识事实或来源文件名。
                fact = next(line.lstrip("- ") for line in hit["snippet"].splitlines() if "热插拔" in line)
                answer = f"模拟回答：{fact} 来源：{hit['source']}（{hit['chunk_id']}）。"
            reply = AIMessage(content=answer)
        else:
            name, arguments = by_question[messages[-1].content]
            calls.append(name)
            reply = AIMessage(content="", tool_calls=[{
                "name": name, "args": arguments, "id": f"knowledge_{len(calls)}",
            }])
        return ChatResult(generations=[ChatGeneration(message=reply)])

    model = ChatOpenAI(model="local-test", api_key="test-only", base_url="https://example.invalid")
    # 两个工具共用同一个tools节点，不为每个工具另建条件边。
    graph = build_graph(model, tools=[lookup_order, search_faq])
    service = ConversationService()
    with (
        patch.object(chat_api, "conversation_service", service),
        patch.object(llm_service, "chat_with_messages", side_effect=make_graph_chat(graph)),
        patch.object(llm_service, "model", "local-mock"),
        patch.object(ChatOpenAI, "_agenerate", new=fake_generate),
    ):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://local-test") as client:
            for index, (question, expected_tool, _) in enumerate(cases):
                response = await client.post("/api/chat/conversation", json={
                    "conversation_id": f"knowledge-demo-{index}", "message": question,
                })
                assert response.status_code == 200
                assert calls[-1] == expected_tool
                body = response.json()
                if index == 0:
                    assert "SF1234567890" in body["answer"]
                elif index == 1:
                    hit = results[-1]["results"][0]
                    assert hit["source"] == "products.md"
                    assert "支持五脚轴热插拔" in body["answer"]
                    assert hit["chunk_id"] in body["answer"]
                else:
                    assert results[-1]["found"] is False
                    assert "无法确认" in body["answer"]
                print("问题：", question)
                print("模拟Tool Call名称：", calls[-1])
                print("HTTP：", response.status_code, body["answer"])
    assert len(calls) == len(results) == 3
    print("三例检查通过；检索仍是正式n-gram，未调用真实模型。")


if __name__ == "__main__":
    asyncio.run(main())
