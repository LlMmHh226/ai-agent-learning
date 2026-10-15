# 课程：step_18b_trim_history_slice.md；访问范围：本地运行（无外部模型请求）。
from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
)


def main() -> None:
    service = ConversationService()
    conversation_id = "trim-demo"
    history = service._get_history(conversation_id)

    for turn in range(1, MAX_HISTORY_TURNS + 1):
        history.append({"role": "user", "content": f"U{turn}"})
        history.append({"role": "assistant", "content": f"A{turn}"})

    # 恰好十轮，正式方法不会删除消息。
    service._trim_history(history)
    print(f"已有十轮：{len(history)} 条，首轮={history[1]['content']}、{history[2]['content']}")

    # 按正式 chat() 的顺序模拟本轮过程，省略真实模型请求。
    history.append({"role": "user", "content": "订单到哪了？"})
    model_messages = service._build_model_messages(conversation_id, history)
    print(f"追加本轮 user、送模型前：history={len(history)} 条，model_messages={len(model_messages)} 条")

    answer = "模拟回答：订单正在运输。"
    history.append({"role": "assistant", "content": answer})
    print(f"追加本轮 assistant 后：history={len(history)} 条")

    max_regular_messages = MAX_HISTORY_TURNS * 2
    stop_index = len(history) - max_regular_messages
    removed_contents = [
        item["content"] for item in history[1:-max_regular_messages]
    ]
    print(f"切片 history[1:-{max_regular_messages}] 等价于 history[1:{stop_index}]")
    print(f"即将删除：{removed_contents}")

    trim_return = service._trim_history(history)
    print(f"裁剪后：history={len(history)} 条")
    print(f"system 仍在索引0：{history[0]['role'] == 'system'}")
    print(f"最早保留：{history[1]['content']}、{history[2]['content']}")
    print(f"最新保留：{history[-2]['content']} / {history[-1]['content']}")
    print(f"方法返回值：{trim_return}")
    print(f"原会话字典也已变为：{len(service.histories[conversation_id])} 条")
    print(f"本次请求副本仍有：{len(model_messages)} 条（history 的删除不影响它）")


if __name__ == "__main__":
    main()
