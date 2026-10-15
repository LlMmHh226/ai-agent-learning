# 课程：step_18c_structured_fact_retention.md；访问范围：本地运行（无外部模型请求）。
from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
)


def main() -> None:
    service = ConversationService()
    conversation_id = "order-memory-demo"
    history = service._get_history(conversation_id)

    message = "请查询订单10001"
    history.append({"role": "user", "content": message})
    # 模拟一次成功回复后的正式顺序，不调用聊天模型或订单工具。
    service._remember_facts(conversation_id, message)
    history.append({"role": "assistant", "content": "模拟回答：已查询订单10001"})
    service._trim_history(history)
    print(f"首轮记录事实：{service.facts[conversation_id]}")

    # 累计十一轮，使含订单号的第一轮离开十轮窗口。
    for turn in range(2, MAX_HISTORY_TURNS + 2):
        message = f"第{turn}轮闲聊"
        history.append({"role": "user", "content": message})
        service._remember_facts(conversation_id, message)
        history.append({"role": "assistant", "content": f"第{turn}轮模拟回答"})
        service._trim_history(history)

    print(f"裁剪后历史条数：{len(history)}")
    print(f"原订单正文仍在历史中：{any('10001' in item['content'] for item in history)}")
    print(f"裁剪后事实仍在：{service.facts[conversation_id]}")

    history.append({"role": "user", "content": "它的物流单号是什么？"})
    model_messages = service._build_model_messages(conversation_id, history)
    print(f"下一轮user：{model_messages[-1]['content']}")
    print(f"下一轮system已注入订单号：{'当前关注的订单编号是 10001' in model_messages[0]['content']}")
    print(f"保存的原system被修改：{'10001' in history[0]['content']}")
    print(f"system新增事实：{model_messages[0]['content'].splitlines()[-1]}")


if __name__ == "__main__":
    main()
