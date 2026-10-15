# 课程：step_20k_graph_conversation.md；访问范围：本地运行（无外部模型请求）。
"""20K：用薄适配函数把图接到原会话服务；仅本地演示，正式接口未迁移。"""

import asyncio
import json
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage, convert_to_messages
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

from app.services.conversation_service import ConversationService, llm_service
from learning.frameworks.step_20i_tool_loop_graph import build_graph


def make_graph_chat(graph):
    """graph来自build_graph；返回签名与chat_with_messages相同的异步适配函数。"""
    async def graph_chat_with_messages(messages: list[dict[str, str]]) -> str:
        """messages来自ConversationService；图返回State后取正文交回会话服务。

        convert_to_messages把role/content字典转为消息对象，不替代facts组装。
        不额外添加system，否则可能丢失或重复服务已组装的订单背景。
        """
        result = await graph.ainvoke(
            {"messages": convert_to_messages(messages)},
            config={"recursion_limit": 6},
        )
        final_message = result["messages"][-1]
        if not isinstance(final_message, AIMessage) or final_message.tool_calls:
            raise ValueError("图没有返回最终回答消息。")
        if not isinstance(final_message.content, str) or not final_message.content.strip():
            raise ValueError("图没有返回非空正文。")
        return final_message.content
    return graph_chat_with_messages


async def main() -> None:
    """无参数，临时替换模型执行入口演示两轮会话，不请求模型。"""
    service = ConversationService()
    observed_inputs = []

    async def fake_generate(model, messages, *args, **kwargs):
        """模型生成的本地替身；固定选择10001，仅验证传递而非模型理解。"""
        observed_inputs.append(list(messages))
        if isinstance(messages[-1], ToolMessage):
            order = json.loads(messages[-1].content)
            reply = AIMessage(content="模拟回答：物流单号为" + order["tracking_number"] + "。")
        else:
            assert any("10001" in str(item.content) for item in messages)
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_order", "args": {"order_id": "10001"},
                "id": f"call_{len(observed_inputs)}",
            }])
        return ChatResult(generations=[ChatGeneration(message=reply)])

    model = ChatOpenAI(model="local-test", api_key="test-only", base_url="https://example.invalid")
    graph_chat = make_graph_chat(build_graph(model))
    # 只在本脚本with作用域替换单例方法，退出后恢复；没有修改正式源代码。
    with patch.object(ChatOpenAI, "_agenerate", new=fake_generate), patch.object(llm_service, "chat_with_messages", side_effect=graph_chat):
        first = await service.chat("c1", "请查询订单10001的物流单号。")
        assert service.facts["c1"]["current_order_id"] == "10001"
        print("第一轮回答：", first)
        print("第一轮保存的facts：", service.facts["c1"])

        # 构造足够多的普通历史，再调用正式裁剪；不模拟十次模型对话。
        history = service.histories["c1"]
        for index in range(10):
            history.extend([
                {"role": "user", "content": f"闲聊{index}"},
                {"role": "assistant", "content": "模拟闲聊回复"},
            ])
        service._trim_history(history)
        assert len(history) == 21
        assert not any("10001" in item["content"] for item in history)

        start = len(observed_inputs)
        answer = await service.chat("c1", "它的物流单号是什么？")
        graph_input = observed_inputs[start]
        assert "10001" in graph_input[0].content
        assert graph_input[-1].content == "它的物流单号是什么？"
        assert [len(items) for items in observed_inputs[start:]] == [22, 24]
        assert len(service.histories["c1"]) == 21
        assert all(item["role"] in ("system", "user", "assistant") for item in service.histories["c1"])
        assert "10001" not in service.histories["c1"][0]["content"]
        assert service.histories["c1"][-1]["content"] == answer
        print("原订单消息已裁剪；图的system消息仍含10001。")
        print("追问的两次模型输入：22条、24条；保存历史：21条。")
        print("第二轮回答：", answer)

    # 验证图异常仍交回正式服务处理，失败输入回退且不记新事实。
    failed_graph = type("FailedGraph", (), {})()
    async def fail(*args, **kwargs):
        raise TimeoutError("本地模拟")
    failed_graph.ainvoke = fail
    with patch.object(llm_service, "chat_with_messages", side_effect=make_graph_chat(failed_graph)):
        try:
            await service.chat("failed", "请查询订单10002")
        except TimeoutError:
            assert "failed" not in service.facts
            assert len(service.histories["failed"]) == 1
        else:
            raise AssertionError("预期图错误向会话服务传播。")
    print("本地检查通过：事实保留、消息传递、历史裁剪和异常回退。")


if __name__ == "__main__":
    asyncio.run(main())
