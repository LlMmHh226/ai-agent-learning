# 课程：step_20l_http_graph_demo.md；访问范围：本地运行（无外部模型请求）。
"""20L：进程内HTTP请求经过正式路由/会话/图；模型模拟，不监听端口。"""

import asyncio
import json
from unittest.mock import patch

import httpx
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

from main import app
import app.api.chat as chat_api
from app.services.conversation_service import ConversationService, llm_service
from learning.frameworks.step_20i_tool_loop_graph import build_graph
from learning.frameworks.step_20k_graph_conversation import make_graph_chat


async def main() -> None:
    """无参数演示入口；发两轮HTTP请求并核对校验、会话隔离和失败响应。"""
    service = ConversationService()
    seen = []

    async def fake_generate(model, messages, *args, **kwargs):
        """用本地响应替代网络生成；读取消息验证传递，不评价真实模型理解。"""
        seen.append(list(messages))
        if messages[-1].content == "模拟超时":
            raise TimeoutError("本地教学模拟")
        if isinstance(messages[-1], ToolMessage):
            order = json.loads(messages[-1].content)
            reply = AIMessage(content="模拟回答：物流单号为" + order["tracking_number"] + "。")
        elif "10001" in str(messages[0].content) or "10001" in str(messages[-1].content):
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_order", "args": {"order_id": "10001"}, "id": f"http_{len(seen)}",
            }])
        else:
            reply = AIMessage(content="模拟回答：请先提供订单号。")
        return ChatResult(generations=[ChatGeneration(message=reply)])

    model = ChatOpenAI(model="local-test", api_key="test-only", base_url="https://example.invalid")
    graph_chat = make_graph_chat(build_graph(model))
    with (
        patch.object(chat_api, "conversation_service", service),
        patch.object(llm_service, "chat_with_messages", side_effect=graph_chat),
        patch.object(llm_service, "model", "local-mock"),
        patch.object(ChatOpenAI, "_agenerate", new=fake_generate),
    ):
        # ASGITransport直接调用进程内app；不发起真实HTTP网络连接。
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://local-test") as client:
            first = await client.post("/api/chat/conversation", json={
                "conversation_id": "http-c1", "message": "  请查询订单10001的物流单号。  ",
            })
            assert first.status_code == 200
            assert seen[0][-1].content == "请查询订单10001的物流单号。"
            assert service.facts["http-c1"]["current_order_id"] == "10001"
            print("第一轮HTTP：", first.status_code, first.json())

            index = len(seen)
            second = await client.post("/api/chat/conversation", json={
                "conversation_id": "http-c1", "message": "它的物流单号是什么？",
            })
            assert second.status_code == 200
            assert "10001" in seen[index][0].content
            assert second.json() == {
                "conversation_id": "http-c1", "model": "local-mock",
                "answer": "模拟回答：物流单号为SF1234567890。",
            }
            assert len(service.histories["http-c1"]) == 5
            assert all(message["role"] != "tool" for message in service.histories["http-c1"])
            print("第二轮HTTP：", second.status_code, second.json())

            index = len(seen)
            other = await client.post("/api/chat/conversation", json={
                "conversation_id": "http-c2", "message": "它的物流单号是什么？",
            })
            assert other.status_code == 200
            assert not any("10001" in str(message.content) for message in seen[index])
            assert "http-c2" not in service.facts
            print("另一会话：", other.json()["answer"])

            calls_before = len(seen)
            invalid = await client.post("/api/chat/conversation", json={
                "conversation_id": "invalid", "message": "   ",
            })
            assert invalid.status_code == 422
            assert len(seen) == calls_before
            assert "invalid" not in service.histories
            print("空白输入HTTP：", invalid.status_code, "；没有进入模型流程。")

            with patch.object(chat_api.logger, "exception"):
                failed = await client.post("/api/chat/conversation", json={
                    "conversation_id": "failed", "message": "模拟超时",
                })
            assert failed.status_code == 502
            assert failed.json() == {"detail": "AI 服务暂时不可用，请稍后重试"}
            assert len(service.histories["failed"]) == 1
            assert "failed" not in service.facts
            print("模拟超时HTTP：", failed.status_code, failed.json())
    print("检查通过；临时替换已恢复，正式接口代码未修改。")


if __name__ == "__main__":
    asyncio.run(main())
