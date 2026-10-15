# 课程：step_18i_context_regression_eval.md；访问范围：本地运行（无外部模型请求）。
"""第18I步：固定多轮用例，对比正式消息与人工摘要分支的本地数据保留。"""

from app.services.conversation_service import MAX_HISTORY_TURNS, ConversationService
from learning.context.step_18d_summary_memory_role import build_summary_demo_messages


# 用例和预期由人工事先标注。summary_fields是独立的手写输入，不由检查函数生成。
EVALUATION_CASES = [
    {
        "name": "短对话10001",
        "conversation_id": "eval-short-10001",
        "first_message": "请查询订单10001，先查物流，暂不申请退款，核查后再决定怎么处理。",
        "idle_turns": 0,
        "expected_order_id": "10001",
        "expected_preference": "暂不申请退款",
        "expected_pending": "核查后再决定怎么处理",
        "summary_fields": {
            "user_goal": "核查订单物流",
            "user_preference": "先查物流，暂不申请退款",
            "pending_action": "核查后再决定怎么处理",
        },
    },
    {
        "name": "跨窗口10001",
        "conversation_id": "eval-long-10001",
        "first_message": "请查询订单10001，先查物流，暂不申请退款，核查后再决定怎么处理。",
        "idle_turns": MAX_HISTORY_TURNS,
        "expected_order_id": "10001",
        "expected_preference": "暂不申请退款",
        "expected_pending": "核查后再决定怎么处理",
        "summary_fields": {
            "user_goal": "核查订单物流",
            "user_preference": "先查物流，暂不申请退款",
            "pending_action": "核查后再决定怎么处理",
        },
    },
    {
        "name": "隔离会话10002",
        "conversation_id": "eval-other-10002",
        "first_message": "请查询订单10002，先查发货进度，暂不修改收货地址，核查后再决定怎么处理。",
        "idle_turns": MAX_HISTORY_TURNS,
        "expected_order_id": "10002",
        "expected_preference": "暂不修改收货地址",
        "expected_pending": "核查后再决定怎么处理",
        "summary_fields": {
            "user_goal": "核查订单发货进度",
            "user_preference": "先查发货进度，暂不修改收货地址",
            "pending_action": "核查后再决定怎么处理",
        },
    },
]
FOLLOW_UPS = [
    "它的物流单号是什么？",
    "仍按之前的方式处理，核查后下一步怎么办？",
]


def prepare_history(service: ConversationService, case: dict[str, object]) -> None:
    """按固定用例准备成功轮次的历史与订单事实，返回None给main或测试。

    参数：
        service：调用方创建的正式会话服务对象；多个用例共用它，以检查会话隔离。
        case：EVALUATION_CASES中的用例字典，提供会话ID、首轮字符串及闲聊轮数。
            idle_turns为0时保留首轮，为10时使首轮离开最近十轮窗口。
    作用：
        复用正式保存事实和裁剪方法，但只用模拟回答构造完整轮次，不调用chat或模型。
        本函数不生成摘要；人工摘要已在case的summary_fields中事先提供。
    """
    conversation_id = case["conversation_id"]
    history = service._get_history(conversation_id)
    first_message = case["first_message"]
    history.append({"role": "user", "content": first_message})
    service._remember_facts(conversation_id, first_message)
    history.append({"role": "assistant", "content": "模拟回答，仅用于构造历史。"})
    service._trim_history(history)
    for turn in range(case["idle_turns"]):
        history.append({"role": "user", "content": f"闲聊问题{turn}"})
        history.append({"role": "assistant", "content": "模拟回答，仅用于构造历史。"})
        service._trim_history(history)


def compare_follow_up(
    service: ConversationService,
    case: dict[str, object],
    question: str,
) -> dict[str, object]:
    """从同份历史生成正式与学习消息，检查信息位置，再模拟保存本轮回答。

    参数：
        service：main或测试传入的正式会话服务，提供该会话的history与facts。
        case：当前固定用例，含独立的预期编号/偏好/待办和人工摘要字典。
        question：FOLLOW_UPS中的追问字符串；两个方案使用完全相同的问题。
    返回：
        检查报告字典，交给main打印汇总，或交给测试断言。布尔值只表示信息
        进入了预定消息、未跨会话混入、组装未改输入，不表示模型已经答对。
    """
    conversation_id = case["conversation_id"]
    history = service._get_history(conversation_id)
    history.append({"role": "user", "content": question})
    history_before = [dict(item) for item in history]
    facts_before = dict(service.facts[conversation_id])
    summary_fields = case["summary_fields"]
    summary_before = dict(summary_fields)

    baseline_messages = service._build_model_messages(conversation_id, history)
    baseline_before = [dict(item) for item in baseline_messages]
    learning_messages = build_summary_demo_messages(baseline_messages, summary_fields)

    order_text = f"当前关注的订单编号是 {case['expected_order_id']}"
    baseline_user_text = "\n".join(
        item["content"] for item in baseline_messages if item["role"] == "user"
    )
    learning_user_text = learning_messages[-1]["content"]
    learning_all_user_text = "\n".join(
        item["content"] for item in learning_messages if item["role"] == "user"
    )
    isolated = True
    for other_case in EVALUATION_CASES:
        if other_case["expected_order_id"] != case["expected_order_id"]:
            foreign_order = f"当前关注的订单编号是 {other_case['expected_order_id']}"
            if (
                foreign_order in baseline_messages[0]["content"]
                or foreign_order in learning_messages[0]["content"]
                or other_case["expected_order_id"] in baseline_user_text
                or other_case["expected_order_id"] in learning_all_user_text
                or other_case["expected_preference"] in baseline_user_text
                or other_case["expected_preference"] in learning_all_user_text
            ):
                isolated = False

    report = {
        "name": case["name"],
        "question": question,
        "baseline_order": order_text in baseline_messages[0]["content"],
        "learning_order": order_text in learning_messages[0]["content"],
        "baseline_preference": case["expected_preference"] in baseline_user_text,
        "learning_preference": case["expected_preference"] in learning_user_text,
        "baseline_pending": case["expected_pending"] in baseline_user_text,
        "learning_pending": case["expected_pending"] in learning_user_text,
        "isolated": isolated,
        "inputs_unchanged": (
            history == history_before
            and service.facts[conversation_id] == facts_before
            and summary_fields == summary_before
            and baseline_messages == baseline_before
        ),
        "shape_preserved": (
            [item["role"] for item in baseline_messages]
            == [item["role"] for item in learning_messages]
            and baseline_messages[-1]["content"] == question
            and learning_user_text.endswith(f"当前用户问题：\n{question}")
        ),
    }

    # 两个方案完成同一轮后，只模拟保存用户问题与最终回答；不把学习摘要写回history。
    service._remember_facts(conversation_id, question)
    history.append({"role": "assistant", "content": "模拟回答，仅用于准备下一次追问。"})
    service._trim_history(history)
    return report


def main() -> None:
    """无参数；运行三个用例各两次追问并汇总信息存在性，返回None给模块入口。"""
    service = ConversationService()
    reports = []
    # 先准备三个独立会话，使其同时存在于同一个服务中。
    for case in EVALUATION_CASES:
        prepare_history(service, case)
    for case in EVALUATION_CASES:
        for question in FOLLOW_UPS:
            report = compare_follow_up(service, case, question)
            reports.append(report)
            print(f"用例：{report['name']}；追问：{question}")
            print(f"  订单检查 正式/学习：{report['baseline_order']} / {report['learning_order']}")
            print(f"  偏好保留 正式/学习：{report['baseline_preference']} / {report['learning_preference']}")
            print(f"  待办保留 正式/学习：{report['baseline_pending']} / {report['learning_pending']}")
            print(f"  会话隔离：{report['isolated']}；组装输入不变：{report['inputs_unchanged']}；角色与问题保留：{report['shape_preserved']}")

    print(f"固定检查共{len(reports)}次，以下为消息中的信息保留次数：")
    for label, baseline_key, learning_key in (
        ("订单编号", "baseline_order", "learning_order"),
        ("用户偏好", "baseline_preference", "learning_preference"),
        ("未完成事项", "baseline_pending", "learning_pending"),
    ):
        baseline_count = sum(report[baseline_key] for report in reports)
        learning_count = sum(report[learning_key] for report in reports)
        print(f"  {label} 正式/学习：{baseline_count}/{len(reports)} / {learning_count}/{len(reports)}")
    print("人工摘要事先给定；本例不评价自动摘要质量、模型记忆或最终回答正确率。")


if __name__ == "__main__":
    main()
