# 课程：step_18h_context_assembly.md；访问范围：本地运行（无外部模型请求）。
"""第18H步：展示一次订单追问的上下文来源与顺序，只模拟模型请求。"""

import json

from app.services.conversation_service import MAX_HISTORY_TURNS, ConversationService
from app.services.llm_service import AVAILABLE_TOOLS
from app.tools.order_tools import get_order_status
from learning.context.step_18d_summary_memory_role import build_summary_demo_messages
from learning.context.step_18e_summary_trigger import should_summarize
from learning.context.step_18f_tool_result_compression import compress_order_result
from learning.context.step_18g_context_trust_boundary import TOOL_DATA_RULE


def main() -> None:
    """无参数；组装两次模拟模型请求及回答后的保存状态，打印后返回None给模块入口。"""
    service = ConversationService()
    conversation_id = "context-assembly-demo"
    history = service._get_history(conversation_id)
    original_system = history[0]["content"]

    first_message = (
        "请查询订单10001。这个包裹我还没有收到。"
        "我想先查物流，暂不申请退款，核查后再决定怎么处理。"
    )
    history.append({"role": "user", "content": first_message})
    service._remember_facts(conversation_id, first_message)
    history.append({"role": "assistant", "content": "首轮模拟回答：已记录你的诉求。"})
    summary_fields: dict[str, str] = {}
    for turn in range(2, MAX_HISTORY_TURNS + 2):
        history.append({"role": "user", "content": f"第{turn}轮闲聊"})
        history.append({"role": "assistant", "content": f"第{turn}轮模拟回答"})
        if should_summarize(history):
            old_messages = [dict(item) for item in history[1:-(MAX_HISTORY_TURNS * 2)]]
            # 学习扩展：裁剪前原文还在，下面是人工预写的首轮摘要，不是自动生成。
            summary_fields = {
                "user_goal": "核查尚未收到的包裹物流",
                "user_preference": "先查物流，暂不申请退款",
                "pending_action": "取得核查结果后，再由用户决定处理方式",
            }
            print(f"请求前准备人工摘要，待删原文共{len(old_messages)}条。")
        service._trim_history(history)

    print(f"请求前history条数：{len(history)}")
    print(f"首轮完整原话仍在history：{any(item['content'] == first_message for item in history)}")
    print(f"独立facts内层字典：{service.facts[conversation_id]}")

    current_question = "它现在是什么状态，物流单号是什么？仍按我之前的方式处理。"
    history.append({"role": "user", "content": current_question})
    # 正式方法：复制历史，并把facts中的订单号加入system副本。
    model_messages = service._build_model_messages(conversation_id, history)
    print(f"追加本次user后history条数：{len(history)}")
    print(f"正式model_messages的system含订单号：{'当前关注的订单编号是 10001' in model_messages[0]['content']}")
    print(f"正式model_messages包含退款偏好：{any('暂不申请退款' in item['content'] for item in model_messages)}")

    # 以下是学习扩展：把人工摘要加入当前user正文，通用工具数据规则加入system副本。
    summary_model_messages = build_summary_demo_messages(model_messages, summary_fields)
    summary_model_messages[0]["content"] += f"\n{TOOL_DATA_RULE}"
    working_messages: list[dict[str, object]] = [dict(item) for item in summary_model_messages]
    tool_names = [tool["function"]["name"] for tool in AVAILABLE_TOOLS]
    print(f"第一次模拟模型请求：messages共{len(working_messages)}条")
    print(f"第0条角色：{working_messages[0]['role']}，最后一条角色：{working_messages[-1]['role']}")
    print(f"独立tools参数中的工具名：{tool_names}")
    print("独立tool_choice参数：auto")
    print("当前user正文（包含学习摘要）：")
    print(working_messages[-1]["content"])

    # 模拟模型要求订单工具。真实调用参数由模型生成，本例从facts读取编号构造样例。
    order_id = service.facts[conversation_id]["current_order_id"]
    tool_call_id = "demo-context-order-10001"
    working_messages.append(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "get_order_status",
                        "arguments": json.dumps({"order_id": order_id}),
                    },
                }
            ],
        }
    )
    tool_result = get_order_status(order_id)  # 正式函数，本地FAKE_ORDERS数据。
    compact_result = compress_order_result(tool_result)  # 学习扩展，正式Tool Loop尚未压缩。
    working_messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(compact_result, ensure_ascii=False),
        }
    )
    print(f"第二次模拟模型请求：messages共{len(working_messages)}条")
    print(f"最后三条角色：{[item['role'] for item in working_messages[-3:]]}")
    print(f"工具结果正文：{working_messages[-1]['content']}")
    print(f"此时保存的history仍为：{len(history)}条")
    print(f"此时正式model_messages仍为：{len(model_messages)}条")

    # 仅由本地数据拼接一个模拟回答；真实answer来自chat_with_messages的模型返回值。
    answer = (
        f"模拟回答：订单{order_id}状态为{compact_result['status']}，"
        f"物流单号为{compact_result['tracking_number']}。"
    )
    service._remember_facts(conversation_id, current_question)
    history.append({"role": "assistant", "content": answer})
    print(f"保存最终assistant后history条数：{len(history)}")
    service._trim_history(history)
    print(f"回答后裁剪，history条数：{len(history)}")
    print(f"history包含临时tool消息吗：{any(item['role'] == 'tool' for item in history)}")
    print(f"history包含临时Tool Call吗：{any('tool_calls' in item for item in history)}")
    print(f"保存的原system保持不变：{history[0]['content'] == original_system}")
    print("模型请求均为本地模拟；没有发送messages或tools，也没有验证模型工具选择或回答。")


if __name__ == "__main__":
    main()
