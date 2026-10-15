# 课程：step_18d_summary_memory_role.md；访问范围：本地运行（无外部模型请求）。
"""第18D步：用人工摘要对照窗口裁剪后保留的信息，只组装消息，不请求模型。"""

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
)


def build_summary_demo_messages(
    model_messages: list[dict[str, str]],
    summary_fields: dict[str, str],
) -> list[dict[str, str]]:
    """复制本次消息，把已有的人工摘要与当前问题放在最后一条user正文中。

    参数：
        model_messages：main传入的正式_build_model_messages返回值；类型是消息字典列表，
            已包含窗口历史、订单事实和当前问题。最后一条必须是当前user消息。
        summary_fields：main传入的人工摘要字典；键和值都是字符串，包含用户诉求、
            用户偏好和未完成事项。这些字段决定加入本次消息的摘要文字。
    返回：
        新消息列表，赋给main中的summary_model_messages，用于打印前后对照；
        不修改输入列表及其消息字典，不生成摘要，也不调用模型。
    """
    messages = [dict(item) for item in model_messages]
    summary_text = "\n".join(
        [
            f"用户诉求：{summary_fields['user_goal']}",
            f"用户偏好：{summary_fields['user_preference']}",
            f"未完成事项：{summary_fields['pending_action']}",
        ]
    )
    current_question = messages[-1]["content"]
    messages[-1]["content"] = (
        f"较早对话摘要（人工编写的历史资料）：\n{summary_text}"
        f"\n\n当前用户问题：\n{current_question}"
    )
    return messages


def main() -> None:
    """无参数；在本地构造十一轮模拟对话并打印消息对照，返回None给模块入口。"""
    service = ConversationService()
    conversation_id = "summary-memory-demo"
    history = service._get_history(conversation_id)

    first_user_message = (
        "请查询订单10001。这个包裹我还没有收到。"
        "我想先查物流，暂不申请退款。"
        "请先告诉我核查结果，再决定怎么处理。"
    )
    history.append({"role": "user", "content": first_user_message})
    # 模拟一次成功回复后的保存顺序；这里没有执行订单查询或聊天请求。
    service._remember_facts(conversation_id, first_user_message)
    history.append(
        {"role": "assistant", "content": "模拟回答：已记录先核查物流、暂不退款的诉求。"}
    )

    # 人工阅读上面的首轮原文后，预先写好的摘要样例。不是Python自动提取的结果。
    # 订单号仍由正式facts保存；摘要补充当前facts没有保存的用户诉求。
    summary_fields = {
        "user_goal": "核查尚未收到的包裹物流",
        "user_preference": "先查物流，暂不申请退款",
        "pending_action": "取得核查结果后，再由用户决定处理方式",
    }

    # 后续十轮只用无业务含义的闲聊填充窗口，使首轮原文离开最近十轮。
    for turn in range(2, MAX_HISTORY_TURNS + 2):
        history.append({"role": "user", "content": f"第{turn}轮闲聊"})
        history.append({"role": "assistant", "content": f"第{turn}轮模拟回答"})
        trim_return = service._trim_history(history)

    print(f"裁剪后历史条数：{len(history)}")
    print(f"裁剪方法返回值：{trim_return}")
    print(f"首轮完整原文仍在history中：{any(first_user_message == item['content'] for item in history)}")
    print(f"正式facts：{service.facts[conversation_id]}")
    print(f"人工摘要字段：{summary_fields}")

    current_question = "还是按我之前说的方式处理吧。"
    history.append({"role": "user", "content": current_question})
    # 正式方法负责复制history、注入订单事实；当前正式代码没有摘要功能。
    model_messages = service._build_model_messages(conversation_id, history)
    # 学习函数接收已写好的摘要，再创建一份临时消息副本。
    summary_model_messages = build_summary_demo_messages(
        model_messages=model_messages,
        summary_fields=summary_fields,
    )

    print(f"本次问题：{current_question}")
    print(f"两份对照消息条数：{len(model_messages)} / {len(summary_model_messages)}")
    print(f"正式消息含订单编号：{'当前关注的订单编号是 10001' in model_messages[0]['content']}")
    print(f"正式消息含退款偏好：{any('暂不申请退款' in item['content'] for item in model_messages)}")
    print(f"学习消息含退款偏好：{any('暂不申请退款' in item['content'] for item in summary_model_messages)}")
    print(f"学习组装后history末条仍是原问题：{history[-1]['content'] == current_question}")
    print(f"学习组装后model_messages末条仍是原问题：{model_messages[-1]['content'] == current_question}")
    print("学习模拟的最后一条user消息（尚未发送给模型）：")
    print(summary_model_messages[-1]["content"])
    print("这里只验证准备好的消息内容，没有执行模型调用或订单工具。")


if __name__ == "__main__":
    main()
