"""固定多轮输入的消息数据回归检查，不调用真实模型。"""

from copy import deepcopy
import unittest

from app.services.conversation_service import ConversationService
from learning.context.step_18i_context_regression_eval import (
    EVALUATION_CASES,
    FOLLOW_UPS,
    compare_follow_up,
    prepare_history,
)


class ContextRegressionEvalTests(unittest.TestCase):
    def test_short_history_keeps_context_in_both_versions(self) -> None:
        """无参数；验证未裁剪时已有能力不退化，返回None给测试运行器。"""
        service = ConversationService()
        case = deepcopy(EVALUATION_CASES[0])
        prepare_history(service, case)
        for question in FOLLOW_UPS:
            report = compare_follow_up(service, case, question)
            self.assertTrue(report["baseline_order"])
            self.assertTrue(report["learning_order"])
            self.assertTrue(report["baseline_preference"])
            self.assertTrue(report["learning_preference"])
            self.assertTrue(report["baseline_pending"])
            self.assertTrue(report["learning_pending"])
            self.assertTrue(report["inputs_unchanged"])
            self.assertTrue(report["shape_preserved"])

    def test_trimmed_history_keeps_order_and_summary_context_across_follow_ups(self) -> None:
        """无参数；验证跨窗口的同组追问，返回None给测试运行器。"""
        service = ConversationService()
        case = deepcopy(EVALUATION_CASES[1])
        prepare_history(service, case)
        for question in FOLLOW_UPS:
            report = compare_follow_up(service, case, question)
            self.assertTrue(report["baseline_order"])
            self.assertTrue(report["learning_order"])
            self.assertFalse(report["baseline_preference"])
            self.assertFalse(report["baseline_pending"])
            self.assertTrue(report["learning_preference"])
            self.assertTrue(report["learning_pending"])
            self.assertTrue(report["inputs_unchanged"])
            self.assertTrue(report["shape_preserved"])

    def test_two_conversations_do_not_mix_orders_or_preferences(self) -> None:
        """无参数；验证同一服务里的两个会话各取自己的数据，返回None给测试运行器。"""
        service = ConversationService()
        cases = deepcopy(EVALUATION_CASES[1:])
        for case in cases:
            prepare_history(service, case)
        for case in cases:
            report = compare_follow_up(service, case, FOLLOW_UPS[0])
            self.assertTrue(report["isolated"])
            self.assertTrue(report["learning_order"])
            self.assertTrue(report["learning_preference"])
        self.assertEqual(service.facts[cases[0]["conversation_id"]]["current_order_id"], "10001")
        self.assertEqual(service.facts[cases[1]["conversation_id"]]["current_order_id"], "10002")

    def test_incorrect_handwritten_summary_is_detected_by_fixed_expectation(self) -> None:
        """无参数；故意改错摘要，检查事先标注的偏好预期能发现遗漏，返回None。"""
        service = ConversationService()
        case = deepcopy(EVALUATION_CASES[1])
        case["summary_fields"]["user_preference"] = "用户已同意立即退款"
        prepare_history(service, case)

        report = compare_follow_up(service, case, FOLLOW_UPS[0])

        self.assertFalse(report["learning_preference"])
        self.assertTrue(report["learning_order"])
        self.assertTrue(report["inputs_unchanged"])

    def test_foreign_conversation_content_in_history_is_detected(self) -> None:
        """无参数；故意把其它会话文字混入历史，验证隔离检查会报告False，返回None。"""
        service = ConversationService()
        case = deepcopy(EVALUATION_CASES[1])
        prepare_history(service, case)
        service.histories[case["conversation_id"]][1]["content"] = (
            "订单10002，先查发货进度，暂不修改收货地址。"
        )

        report = compare_follow_up(service, case, FOLLOW_UPS[0])

        self.assertFalse(report["isolated"])
        self.assertTrue(report["learning_order"])


if __name__ == "__main__":
    unittest.main()
