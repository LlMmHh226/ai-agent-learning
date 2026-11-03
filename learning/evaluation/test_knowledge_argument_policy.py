"""知识库自由文本参数的离线检查；模型模拟，工具和HTTP路径实际本地执行。"""

import json
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from openai.types.chat import ChatCompletionMessage

from learning.evaluation.step_02_run_first_case import (
    ROOT, check_tool_policy, collect_case, llm_service,
)


class KnowledgeArgumentTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "tool_policy": "required",
            "argument_match": "nonempty_query",
            "required_tool_call": {
                "name": "search_knowledge_base",
                "arguments": {"query": "星云机械键盘支持热插拔吗？"},
            },
            "tool_result_fields": {"found": True},
        }

    def checks_for(self, arguments, name="search_knowledge_base"):
        tool = {"name": name, "arguments": arguments, "result": {"found": True}}
        return check_tool_policy(self.expected, [], [tool])

    def test_reworded_query_is_not_rejected_for_different_text(self):
        checks = self.checks_for({"query": "星云机械键盘可以直接换轴吗？"})
        self.assertTrue(checks["required_tool_and_arguments"])
        self.assertTrue(checks["tool_result_facts"])

    def test_invalid_query_structure_is_rejected(self):
        for arguments in ({}, {"query": "  "}, {"query": None}, {"query": 7},
                          {"query": "键盘", "order_id": "10001"}, "键盘", []):
            with self.subTest(arguments=arguments):
                self.assertFalse(self.checks_for(arguments)["required_tool_and_arguments"])

    def test_wrong_tool_is_rejected(self):
        self.assertFalse(self.checks_for({"query": "键盘"}, "get_order_status")["required_tool_and_arguments"])

    def test_existing_cases_keep_exact_argument_matching(self):
        self.expected.pop("argument_match")
        self.expected["required_tool_call"] = {"name": "get_order_status", "arguments": {"order_id": "10001"}}
        self.assertTrue(self.checks_for({"order_id": "10001"}, "get_order_status")["required_tool_and_arguments"])
        self.assertFalse(self.checks_for({"order_id": "10002"}, "get_order_status")["required_tool_and_arguments"])

    def test_relaxed_matching_cannot_apply_to_orders_or_history_reuse(self):
        for name, policy in (("get_order_status", "required"), ("search_knowledge_base", "optional")):
            with self.subTest(name=name, policy=policy):
                expected = deepcopy(self.expected)
                expected["required_tool_call"]["name"] = name
                expected["tool_policy"] = policy
                with self.assertRaisesRegex(ValueError, "仅用于required"):
                    check_tool_policy(expected, [], [])

    def test_unknown_argument_rule_is_rejected(self):
        self.expected["argument_match"] = "unknown"
        with self.assertRaisesRegex(ValueError, "argument_match"):
            self.checks_for({"query": "键盘"})


class KnowledgeCollectorTests(unittest.IsolatedAsyncioTestCase):
    async def test_reworded_query_executes_real_tool_but_bad_answer_stays_pending(self):
        data = json.loads((ROOT / "learning/evaluation/cases/agent_baseline.json").read_text(encoding="utf-8"))
        case = next(item for item in data["cases"] if item["id"] == "knowledge_keyboard_hot_swap")
        query = "星云机械键盘换轴是否需要焊接，是否支持热插拔？"
        calls = []

        async def offline_response(**kwargs):
            calls.append(len(kwargs["messages"]))
            if len(calls) == 1:
                message = ChatCompletionMessage(role="assistant", tool_calls=[{
                    "id": "offline-knowledge", "type": "function",
                    "function": {"name": "search_knowledge_base", "arguments": json.dumps({"query": query}, ensure_ascii=False)},
                }])
            else:
                # 故意答错，验证机械通过不会自动认定语义通过。
                message = ChatCompletionMessage(role="assistant", content="离线错误示例：换轴需要焊接。")
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)

        with patch.object(llm_service.client.chat.completions, "create", new=offline_response):
            report = await collect_case(case)
        self.assertEqual(calls, [2, 4])
        self.assertEqual(report["executed_tools"][0]["arguments"], {"query": query})
        self.assertEqual(report["executed_tools"][0]["result"]["results"][0]["source"], "products.md")
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["human_review"]["status"], "pending")
        self.assertEqual(report["task_verdict"], "pending")
        self.assertEqual(report["grading_policy_version"], 3)


if __name__ == "__main__":
    unittest.main()
