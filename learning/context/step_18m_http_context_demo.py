# 课程：step_18m_http_context_demo.md；访问范围：本地运行（无外部模型请求）。
"""第18M步：通过进程内HTTP客户端运行正式路由与Tool Loop，模型网络响应为模拟。"""

import json
from copy import deepcopy
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from openai.types.chat import ChatCompletionMessage

from app.services.conversation_service import MAX_HISTORY_TURNS, conversation_service, llm_service
from main import app


def main() -> None:
    """无参数；发送固定HTTP对话、观察模型输入快照和响应JSON，返回None给模块入口。"""
    conversation_id = "http-context-demo"
    state = {"phase": "", "request_no": 0}
    snapshots = []
    conversation_service.clear(conversation_id)

    async def simulate_create(**request_parameters: Any) -> SimpleNamespace:
        """在SDK入口复制实际参数，再给正式Tool Loop返回本地模拟对象。

        参数：request_parameters收集正式create传入的关键字参数；仅读取messages。
        返回：包含choices[0].message的模拟响应。订单查询与最后追问的首次请求
            预设Tool Call，后续读取正式工具结果拼接模拟答复，不做真实模型推理。
        """
        state["request_no"] += 1
        messages = request_parameters["messages"]
        snapshots.append(
            {
                "phase": state["phase"],
                "request_no": state["request_no"],
                "messages": deepcopy(messages),
            }
        )
        if state["phase"] in ("order", "follow_up") and state["request_no"] == 1:
            message = ChatCompletionMessage(
                role="assistant",
                content=None,
                tool_calls=[
                    {
                        "id": f"demo-http-{state['phase']}",
                        "type": "function",
                        "function": {
                            "name": "get_order_status",
                            "arguments": json.dumps({"order_id": "10001"}),
                        },
                    }
                ],
            )
        elif state["phase"] in ("order", "follow_up"):
            tool_result = json.loads(messages[-1]["content"])
            message = ChatCompletionMessage(
                role="assistant",
                content=(
                    f"模拟回答：订单{tool_result['order_id']}状态为{tool_result['status']}，"
                    f"物流单号为{tool_result['tracking_number']}。"
                ),
            )
        else:
            message = ChatCompletionMessage(role="assistant", content="模拟回答：已收到。")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)

    with (
        TestClient(app) as client,
        patch.object(llm_service.client.chat.completions, "create", side_effect=simulate_create),
    ):
        def post_message(message: str, phase: str) -> dict[str, str]:
            """向正式多轮路由提交一个用户轮，返回响应字典。

            参数：message为main提供的当前问题字符串，phase为模拟响应场景标签。
            返回：正式ConversationChatResponse转换的JSON字典；调用方打印或检查。
            phase仅控制本地模拟，不传给HTTP接口；接口仍只有会话ID与message。
            """
            state["phase"] = phase
            state["request_no"] = 0
            payload = {"conversation_id": conversation_id, "message": message}
            response = client.post("/api/chat/conversation", json=payload)
            response.raise_for_status()
            result = response.json()
            if phase != "idle":
                print(f"HTTP请求：{json.dumps(payload, ensure_ascii=False)}")
                print(f"HTTP状态：{response.status_code}；响应：{json.dumps(result, ensure_ascii=False)}")
            return result

        post_message("请查询订单10001", "order")
        post_message("  暂不申请退款。  ", "preference")
        for turn in range(MAX_HISTORY_TURNS):
            post_message(f"闲聊问题{turn}", "idle")

        history = conversation_service.histories[conversation_id]
        print(f"十二轮完成，history条数：{len(history)}")
        print(f"原偏好声明仍在history：{any('暂不申请退款' in item['content'] for item in history)}")
        print(f"正式facts：{conversation_service.facts[conversation_id]}")
        question = "它的物流单号是什么？仍按之前的方式处理。"
        final_response = post_message(question, "follow_up")

    preference_request = next(item for item in snapshots if item["phase"] == "preference")
    follow_up_requests = [item for item in snapshots if item["phase"] == "follow_up"]
    print(f"声明轮送模型的原user正文：{preference_request['messages'][-1]['content']!r}")
    print("最终追问第一次准备的user正文：")
    print(follow_up_requests[0]["messages"][-1]["content"])
    print(f"最终追问两次准备的消息条数：{[len(item['messages']) for item in follow_up_requests]}")
    print(f"第二次准备的末两条角色：{[item['role'] for item in follow_up_requests[1]['messages'][-2:]]}")
    print(f"HTTP响应answer包含本地工具物流号：{'SF1234567890' in final_response['answer']}")
    print(f"保存的当前user仍是原问题：{history[-2]['content'] == question}")
    print(f"最终保存的history条数：{len(history)}")
    print(f"13个HTTP用户轮，共经过{len(snapshots)}次模拟模型请求入口。")
    print("HTTP应用内调用、路由与服务均真实执行；模型响应为预设模拟，无真实模型请求或退款。")
    # 只清理本演示在当前Python进程创建的会话，不操作外部服务。
    conversation_service.clear(conversation_id)


if __name__ == "__main__":
    main()
