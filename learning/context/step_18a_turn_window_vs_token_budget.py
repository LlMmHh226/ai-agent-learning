# 课程：step_18a_turn_window_vs_token_budget.md；访问范围：本地运行（无外部模型请求）。
from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
)
from app.services.llm_service import DEFAULT_SYSTEM_PROMPT


def main() -> None:
    examples = [
        ("短消息", "物流没动静"),
        ("长消息", "物流" * 900),
    ]

    for label, message_text in examples:
        service = ConversationService()
        history = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
        for _ in range(MAX_HISTORY_TURNS):
            history.append({"role": "user", "content": message_text})
            history.append({"role": "assistant", "content": message_text})

        service._trim_history(history)
        stored_message_count = len(history)
        stored_characters = sum(len(item["content"]) for item in history)

        # 正式 chat() 也是先追加本轮 user，再组装消息并调用模型；
        # 模型返回 assistant 消息之后才裁剪 history。
        history.append({"role": "user", "content": "订单到哪了？"})
        model_messages = service._build_model_messages("演示会话", history)
        request_characters = sum(
            len(item["content"]) for item in model_messages
        )

        print(f"{label}：每条示例消息 {len(message_text)} 个字符")
        print(
            f"裁剪后保存：{MAX_HISTORY_TURNS} 轮，"
            f"messages={stored_message_count} 条（含 system），"
            f"消息正文字符={stored_characters}"
        )
        print(
            f"追加本轮 user 后、送模型前：messages={len(model_messages)} 条，"
            f"消息正文字符={request_characters}\n"
        )

    print("注意：上面的字符数不是 Token 数；工具 Schema 和工具结果也会影响上下文。")


if __name__ == "__main__":
    main()
