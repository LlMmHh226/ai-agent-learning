# 课程：step_18e_summary_trigger.md；访问范围：本地运行（无外部模型请求）。
"""第18E步：在完整一轮保存后、裁剪前判断是否需要摘要；不请求模型。"""

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
)
from learning.context.step_18d_summary_memory_role import (
    build_summary_demo_messages,
)


def should_summarize(history: list[dict[str, str]]) -> bool:
    """判断完整轮次的历史是否将因窗口限制而删除旧消息。

    参数：
        history：main传入的会话消息字典列表，首条是system，其后是成对的user与
            最终assistant。本函数只在一轮已完整保存、裁剪尚未执行时使用。
    返回：
        bool，赋给main中的needs_summary；普通消息超过最近十轮容量时为True。
        只读取条数，不修改history、不生成摘要，也不调用模型。
    """
    max_regular_messages = MAX_HISTORY_TURNS * 2
    regular_message_count = len(history) - 1
    return regular_message_count > max_regular_messages


def main() -> None:
    """无参数；本地模拟1至11轮并打印首次触发和下一轮消息，返回None给模块入口。"""
    service = ConversationService()
    conversation_id = "summary-trigger-demo"
    history = service._get_history(conversation_id)
    max_regular_messages = MAX_HISTORY_TURNS * 2
    summary_fields: dict[str, str] = {}
    old_messages: list[dict[str, str]] = []

    for turn in range(1, MAX_HISTORY_TURNS + 2):
        if turn == 1:
            user_message = (
                "请查询订单10001。这个包裹我还没有收到。"
                "我想先查物流，暂不申请退款。"
                "请先告诉我核查结果，再决定怎么处理。"
            )
            assistant_message = "模拟回答：已记录先查物流、暂不退款的诉求。"
        else:
            user_message = f"第{turn}轮闲聊"
            assistant_message = f"第{turn}轮模拟回答"

        history.append({"role": "user", "content": user_message})
        # 模拟模型成功后的保存顺序，没有执行网络请求或订单查询。
        service._remember_facts(conversation_id, user_message)
        history.append({"role": "assistant", "content": assistant_message})

        # 新的学习规则放在完整一轮之后、正式裁剪之前；正式chat尚未加入此规则。
        needs_summary = should_summarize(history)
        if turn in (1, MAX_HISTORY_TURNS, MAX_HISTORY_TURNS + 1):
            print(f"第{turn}轮完成、裁剪前：{len(history)}条，触发摘要：{needs_summary}")

        if needs_summary:
            # 与正式_trim_history的删除范围一致，先复制待删除的原文。
            old_messages = [dict(item) for item in history[1:-max_regular_messages]]
            print(f"待删除原文：{len(old_messages)}条，角色：{[item['role'] for item in old_messages]}")
            print(f"待删除的用户原文：{old_messages[0]['content']}")
            # 本例只演示首次触发。下面是人工预写的首轮摘要，未自动提炼或合并旧摘要。
            summary_fields = {
                "user_goal": "核查尚未收到的包裹物流",
                "user_preference": "先查物流，暂不申请退款",
                "pending_action": "取得核查结果后，再由用户决定处理方式",
            }
            print("已准备人工摘要，随后才裁剪history。")

        service._trim_history(history)

    print(f"第11轮裁剪后历史条数：{len(history)}")
    print(f"裁剪后才检查是否触发：{should_summarize(history)}")
    print(f"裁剪后才提取待删原文：{len(history[1:-max_regular_messages])}条")
    print(f"提前复制的原文仍有：{len(old_messages)}条")
    print(f"当前会话订单号：{service.facts[conversation_id]['current_order_id']}")

    current_question = "还是按我之前说的方式处理吧。"
    history.append({"role": "user", "content": current_question})
    model_messages = service._build_model_messages(conversation_id, history)
    summary_model_messages = build_summary_demo_messages(
        model_messages=model_messages,
        summary_fields=summary_fields,
    )
    print(f"下一轮两份消息条数：{len(model_messages)} / {len(summary_model_messages)}")
    print(f"原history末条仍是当前问题：{history[-1]['content'] == current_question}")
    print("下一轮学习消息的user正文（尚未发送给模型）：")
    print(summary_model_messages[-1]["content"])
    print("本步自动判断触发时机；摘要文字仍为人工样例，正式接口没有摘要功能。")


if __name__ == "__main__":
    main()
