"""明确退款偏好的正式会话记忆回归测试，模型响应使用本地模拟。"""

import unittest
from copy import deepcopy
from unittest.mock import AsyncMock, patch

from app.services.conversation_service import (
    MAX_HISTORY_TURNS,
    ConversationService,
    extract_refund_preference,
    llm_service,
)


class RefundPreferenceMemoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_preference_survives_trim_and_only_enters_user_copy(self) -> None:
        """无参数；原文删除后偏好仍进入下轮输入，保存历史不被注入改写；返回None。"""
        service = ConversationService()
        conversation_id = "preference-retention"
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")) as model_mock:
            await service.chat(conversation_id, "请查询订单10001")
            await service.chat(conversation_id, "暂不申请退款。")
            for turn in range(MAX_HISTORY_TURNS):
                await service.chat(conversation_id, f"闲聊问题{turn}")
            history = service.histories[conversation_id]
            self.assertEqual(len(history), 21)
            self.assertFalse(any("暂不申请退款" in item["content"] for item in history))
            self.assertEqual(service.facts[conversation_id]["current_refund_preference"], "暂不申请退款")

            question = "还是按我之前说的方式处理。"
            await service.chat(conversation_id, question)
            sent_messages = model_mock.await_args.args[0]

        self.assertIn("暂不申请退款", sent_messages[-1]["content"])
        self.assertEqual(sent_messages[-1]["role"], "user")
        self.assertTrue(sent_messages[-1]["content"].endswith(question))
        self.assertNotIn("暂不申请退款", sent_messages[0]["content"])
        self.assertEqual(history[-2]["content"], question)
        self.assertNotIn("此前明确表达", history[0]["content"])

    async def test_current_statement_does_not_receive_old_preference_and_updates_after_success(self) -> None:
        """无参数；当前明确改口不重复旧偏好，成功后下一轮读取新值；返回None。"""
        service = ConversationService()
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")) as model_mock:
            await service.chat("changed", "请查询订单10001")
            await service.chat("changed", "暂不申请退款")
            await service.chat("changed", "现在申请退款")
            changed_messages = model_mock.await_args.args[0]
            self.assertEqual(changed_messages[-1]["content"], "现在申请退款")
            self.assertEqual(service.facts["changed"]["current_refund_preference"], "现在申请退款")
            await service.chat("changed", "按刚才说的处理。")
            self.assertIn("现在申请退款", model_mock.await_args.args[0][-1]["content"])

    async def test_question_negation_quote_and_condition_do_not_change_preference(self) -> None:
        """无参数；未知语句、问题及引用等不因关键词被误记，返回None。"""
        service = ConversationService()
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")):
            await service.chat("unchanged", "请查询订单10001")
            await service.chat("unchanged", "暂不申请退款")
            for message in (
                "现在申请退款吗？",
                "我不想现在申请退款",
                "他说‘现在申请退款’",
                "如果明天没到，现在申请退款。",
                "请查询订单10001，暂不申请退款。",
                "它的物流单号是什么？",
            ):
                with self.subTest(message=message):
                    self.assertIsNone(extract_refund_preference(message))
                    await service.chat("unchanged", message)
                    self.assertEqual(service.facts["unchanged"]["current_refund_preference"], "暂不申请退款")
        self.assertEqual(extract_refund_preference("  暂不申请退款。  "), "暂不申请退款")

    async def test_model_failure_does_not_commit_changed_preference_or_history(self) -> None:
        """无参数；网络模型异常时沿用原有回滚，偏好和历史保持此前状态；返回None。"""
        service = ConversationService()
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")):
            await service.chat("failed", "请查询订单10001")
            await service.chat("failed", "暂不申请退款")
        history_before = deepcopy(service.histories["failed"])
        facts_before = dict(service.facts["failed"])
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(side_effect=RuntimeError("模拟故障"))):
            with self.assertRaises(RuntimeError):
                await service.chat("failed", "现在申请退款")
        self.assertEqual(service.histories["failed"], history_before)
        self.assertEqual(service.facts["failed"], facts_before)

    async def test_order_switch_conversation_isolation_and_clear(self) -> None:
        """无参数；换订单不带旧偏好，会话隔离及clear生命周期保持一致；返回None。"""
        service = ConversationService()
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")) as model_mock:
            await service.chat("a", "请查询订单10001")
            await service.chat("a", "暂不申请退款")
            await service.chat("b", "请查询订单10002")
            await service.chat("b", "现在申请退款")
            await service.chat("a", "按之前方式处理。")
            sent_a = model_mock.await_args.args[0][-1]["content"]
            self.assertIn("暂不申请退款", sent_a)
            self.assertNotIn("现在申请退款", sent_a)
            await service.chat("a", "请查询订单10003")
            self.assertEqual(model_mock.await_args.args[0][-1]["content"], "请查询订单10003")
            self.assertNotIn("current_refund_preference", service.facts["a"])
        self.assertTrue(service.clear("b"))
        self.assertNotIn("b", service.facts)
        self.assertNotIn("b", service.histories)

    async def test_preference_without_selected_order_is_not_saved(self) -> None:
        """无参数；未选择订单时不建立有歧义的订单偏好记录；返回None。"""
        service = ConversationService()
        with patch.object(llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")):
            await service.chat("no-order", "暂不申请退款")
        self.assertNotIn("current_refund_preference", service.facts.get("no-order", {}))


if __name__ == "__main__":
    unittest.main()
