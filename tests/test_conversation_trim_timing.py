import unittest
from unittest.mock import AsyncMock, patch

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
    llm_service,
)


class ConversationTrimTimingTests(unittest.IsolatedAsyncioTestCase):
    async def test_oldest_pair_is_removed_after_model_response(self) -> None:
        service = ConversationService()
        history = service._get_history("timing-demo")
        for turn in range(1, MAX_HISTORY_TURNS + 1):
            history.append({"role": "user", "content": f"U{turn}"})
            history.append({"role": "assistant", "content": f"A{turn}"})

        async def simulate_model(messages):
            # 正式 chat() 已追加当前 user，但尚未裁剪已有十轮。
            self.assertEqual(len(messages), 22)
            self.assertEqual(messages[1]["content"], "U1")
            self.assertEqual(messages[-1]["content"], "订单到哪了？")
            self.assertEqual(len(history), 22)
            return "模拟回答"

        with patch.object(
            llm_service,
            "chat_with_messages",
            new=AsyncMock(side_effect=simulate_model),
        ) as model_mock:
            answer = await service.chat("timing-demo", "订单到哪了？")

        self.assertEqual(answer, "模拟回答")
        model_mock.assert_awaited_once()
        self.assertIs(history, service.histories["timing-demo"])
        self.assertEqual(len(history), 21)
        self.assertEqual(history[0]["role"], "system")
        self.assertEqual(history[1]["content"], "U2")
        self.assertEqual(history[-2]["content"], "订单到哪了？")
        self.assertEqual(history[-1]["content"], "模拟回答")


if __name__ == "__main__":
    unittest.main()
