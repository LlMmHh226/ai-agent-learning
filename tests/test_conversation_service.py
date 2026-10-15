import unittest
from unittest.mock import AsyncMock, patch

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
    llm_service,
)


class ConversationHistoryTests(unittest.TestCase):
    def test_trim_history_keeps_system_and_recent_turns(self) -> None:
        service = ConversationService()
        history = service._get_history("test-conversation")

        total_turns = MAX_HISTORY_TURNS + 2
        for index in range(total_turns):
            history.append(
                {
                    "role": "user",
                    "content": f"用户消息{index}",
                }
            )
            history.append(
                {
                    "role": "assistant",
                    "content": f"模型回答{index}",
                }
            )

        service._trim_history(history)

        self.assertEqual(len(history), 1 + MAX_HISTORY_TURNS * 2)
        self.assertEqual(history[0]["role"], "system")
        self.assertEqual(history[1]["content"], "用户消息2")
        self.assertEqual(history[-1]["content"], "模型回答11")

    def test_short_history_is_unchanged(self) -> None:
        service = ConversationService()
        history = service._get_history("short-conversation")
        history.append({"role": "user", "content": "你好"})
        original_history = list(history)

        service._trim_history(history)

        self.assertEqual(history, original_history)

    def test_order_fact_survives_history_trim(self) -> None:
        service = ConversationService()
        service._remember_facts(
            "fact-conversation",
            "请查询订单10001",
        )
        history = service._get_history("fact-conversation")

        for index in range(MAX_HISTORY_TURNS + 2):
            history.append({"role": "user", "content": f"问题{index}"})
            history.append({"role": "assistant", "content": f"回答{index}"})

        service._trim_history(history)

        self.assertEqual(
            service.facts["fact-conversation"]["current_order_id"],
            "10001",
        )

    def test_clear_removes_history_and_facts(self) -> None:
        service = ConversationService()
        service._get_history("clear-conversation")
        service._remember_facts("clear-conversation", "订单10002")

        cleared = service.clear("clear-conversation")

        self.assertTrue(cleared)
        self.assertNotIn("clear-conversation", service.histories)
        self.assertNotIn("clear-conversation", service.facts)


class ConversationFactInjectionTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(
        llm_service,
        "chat_with_messages",
        new_callable=AsyncMock,
    )
    async def test_remembered_order_is_sent_on_follow_up(
        self,
        chat_mock: AsyncMock,
    ) -> None:
        chat_mock.return_value = "测试回答"
        service = ConversationService()

        await service.chat("agent-memory", "请查询订单10001")
        await service.chat("agent-memory", "它的物流单号是什么？")

        second_messages = chat_mock.await_args_list[1].args[0]
        self.assertIn("当前关注的订单编号是 10001", second_messages[0]["content"])


if __name__ == "__main__":
    unittest.main()
