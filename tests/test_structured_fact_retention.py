import unittest
from unittest.mock import AsyncMock, patch

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
    llm_service,
)


class StructuredFactRetentionTests(unittest.IsolatedAsyncioTestCase):
    async def test_order_is_injected_after_original_round_is_trimmed(self) -> None:
        service = ConversationService()
        conversation_id = "retention-test"

        with patch.object(
            llm_service,
            "chat_with_messages",
            new=AsyncMock(return_value="模拟回答"),
        ) as model_mock:
            await service.chat(conversation_id, "请查询订单10001")
            for turn in range(MAX_HISTORY_TURNS):
                await service.chat(conversation_id, f"闲聊问题{turn}")

            history = service.histories[conversation_id]
            self.assertEqual(len(history), 21)
            self.assertFalse(any("10001" in item["content"] for item in history))
            self.assertEqual(service.facts[conversation_id]["current_order_id"], "10001")

            await service.chat(conversation_id, "它的物流单号是什么？")

        sent_messages = model_mock.await_args.args[0]
        self.assertEqual(sent_messages[-1]["content"], "它的物流单号是什么？")
        self.assertIn("当前关注的订单编号是 10001", sent_messages[0]["content"])
        self.assertNotIn("10001", service.histories[conversation_id][0]["content"])


if __name__ == "__main__":
    unittest.main()
