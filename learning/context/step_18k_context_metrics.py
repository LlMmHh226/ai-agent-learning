# 课程：step_18k_context_metrics.md；访问范围：本地运行（无外部模型请求）。
"""第18K步：运行正式会话和Tool Loop，以本地模拟响应观察请求与裁剪指标。"""

import asyncio
import json
import math
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from openai.types.chat import ChatCompletionMessage

from app.services.conversation_service import MAX_HISTORY_TURNS, ConversationService, llm_service


# 下列值只是教学规划，不是当前服务的真实窗口、输出限制或分词规则。
DEMO_WINDOW_TOKENS = 4096
DEMO_OUTPUT_RESERVE = 512
DEMO_FORMAT_RESERVE = 256
DEMO_TOKENS_PER_CHAR = (1.0, 2.0)


def measure_request(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> dict[str, int]:
    """统计本地纯文本请求快照的条数与字符数，不修改输入、不计真实Token。

    参数：
        messages：simulate_create从正式SDK调用参数取得的working_messages；
            包含system、user/assistant历史，以及本轮可能新增的调用和结果。
        tools：同一调用参数中的AVAILABLE_TOOLS列表；这是独立的工具说明参数。
    返回：
        整数字典，由simulate_create加入requests记录。content_chars只数正文；
        messages_json_chars包含消息结构和Tool Call参数，tools_json_chars数工具说明。
        context_json_chars是后两者之和，不再重复加content_chars。JSON长度只是
        本地文本代理量，不等于服务端实际提示词长度、Token数或SDK最终网络字节数。
    """
    content_chars = sum(len(item.get("content") or "") for item in messages)
    messages_json_chars = len(json.dumps(messages, ensure_ascii=False, separators=(",", ":")))
    tools_json_chars = len(json.dumps(tools, ensure_ascii=False, separators=(",", ":")))
    return {
        "message_count": len(messages),
        "content_chars": content_chars,
        "messages_json_chars": messages_json_chars,
        "tools_json_chars": tools_json_chars,
        "context_json_chars": messages_json_chars + tools_json_chars,
    }


async def main() -> None:
    """无参数；模拟12个用户轮，观测正式请求与裁剪，返回None给asyncio.run。"""
    service = ConversationService()
    conversation_id = "context-metrics-demo"
    state = {"user_turn": 0, "model_request": 0, "trim_events": 0}
    requests = []
    trims = []
    original_trim = service._trim_history

    async def simulate_create(**request_parameters: Any) -> SimpleNamespace:
        """接替SDK网络方法，记录参数并返回模拟响应。

        参数：request_parameters收集正式create传入的关键字参数为字典；
            本地只读取messages和tools计数，绝不输出模型配置或密钥。
        返回：带choices[0].message的本地对象，交回正式Tool Loop；第一轮首次
            模拟订单Tool Call，其余请求返回模拟最终回答，不验证真实模型能力。
        """
        state["model_request"] += 1
        metric = measure_request(request_parameters["messages"], request_parameters["tools"])
        requests.append(
            {"user_turn": state["user_turn"], "model_request": state["model_request"], **metric}
        )
        if state["user_turn"] == 1 and state["model_request"] == 1:
            message = ChatCompletionMessage(
                role="assistant",
                content=None,
                tool_calls=[
                    {
                        "id": "demo-metrics-order-10001",
                        "type": "function",
                        "function": {
                            "name": "get_order_status",
                            "arguments": json.dumps({"order_id": "10001"}),
                        },
                    }
                ],
            )
        else:
            message = ChatCompletionMessage(
                role="assistant", content="模拟回答，仅用于观察正式代码流程。"
            )
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)

    def observe_trim(history: list[dict[str, str]]) -> None:
        """接替本实例的裁剪入口，执行原方法后记录实际删除量，返回None。

        参数：history是正式chat在保存最终回答后传入的原历史列表。
        只在条数实际减少时累计一次trim_events，不把每次调用都算成一次删除。
        """
        before_count = len(history)
        original_trim(history)
        removed_messages = before_count - len(history)
        if removed_messages > 0:
            state["trim_events"] += 1
        trims.append(
            {
                "user_turn": state["user_turn"],
                "before_count": before_count,
                "after_count": len(history),
                "removed_messages": removed_messages,
                "trim_events": state["trim_events"],
            }
        )

    # 替换仅在本进程with范围内生效，退出后恢复；正式业务文件没有修改。
    with (
        patch.object(llm_service.client.chat.completions, "create", side_effect=simulate_create),
        patch.object(service, "_trim_history", side_effect=observe_trim),
    ):
        for turn in range(1, MAX_HISTORY_TURNS + 3):
            state["user_turn"] = turn
            state["model_request"] = 0
            if turn == 1:
                question = "订单10001现在是什么状态，物流单号是什么？"
            elif turn == MAX_HISTORY_TURNS + 1:
                question = "物流" * 900  # 1800字符样例，用于观察条数相同但长度变化。
            else:
                question = f"第{turn}轮闲聊"
            await service.chat(conversation_id, question)

    print("每次正式模型请求入口的本地快照（网络由模拟响应接替）：")
    for metric in requests:
        print(
            f"用户轮{metric['user_turn']} 请求{metric['model_request']}："
            f"消息{metric['message_count']}条，正文{metric['content_chars']}字符，"
            f"消息JSON{metric['messages_json_chars']}字符，"
            f"工具说明JSON{metric['tools_json_chars']}字符，"
            f"两者合计{metric['context_json_chars']}字符"
        )
    print("每轮回答保存后的裁剪观察：")
    for metric in trims:
        print(
            f"用户轮{metric['user_turn']}：{metric['before_count']}→{metric['after_count']}条，"
            f"实际删除{metric['removed_messages']}条，累计裁剪{metric['trim_events']}次"
        )
    print(f"用户共{len(trims)}轮，模型请求入口共{len(requests)}次，实际裁剪{state['trim_events']}次。")

    input_budget = DEMO_WINDOW_TOKENS - DEMO_OUTPUT_RESERVE - DEMO_FORMAT_RESERVE
    print(
        f"教学预算：假设窗口{DEMO_WINDOW_TOKENS}，输出预留{DEMO_OUTPUT_RESERVE}，"
        f"格式余量{DEMO_FORMAT_RESERVE}，输入额度{input_budget}。"
    )
    # 只展示首轮两次请求与长消息轮，不把估算用于正式拒答或裁剪。
    for metric in requests:
        if metric["user_turn"] in (1, MAX_HISTORY_TURNS + 1):
            for assumed_rate in DEMO_TOKENS_PER_CHAR:
                estimated_input = math.ceil(metric["context_json_chars"] * assumed_rate)
                print(
                    f"在假设每字符{assumed_rate:g} Token下，用户轮{metric['user_turn']}"
                    f"请求{metric['model_request']}：输入估算{estimated_input}，"
                    f"剩余教学额度{input_budget - estimated_input}。"
                )
    print("上述倍率和窗口为人工教学假设，不是经验区间、安全上界或当前模型设置。")
    print("输出预留没有传给API作为输出上限；没有真实usage、Token计费或费用数据。")


if __name__ == "__main__":
    asyncio.run(main())
