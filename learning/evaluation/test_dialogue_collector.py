"""多轮采集器离线检查：真实会话服务/工具，模型响应模拟，不联网。"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openai.types.chat import ChatCompletionMessage

from learning.evaluation import step_02_run_first_case as runner


def dialogue_case():
    return {
        "id": "offline_order_followup", "method": "POST", "path": "/api/chat/conversation",
        "request": {"conversation_id": "offline-order-followup"},
        "turns": [
            {"message": "请查询订单10001的状态。", "expected": {
                "http_status": 200,
                "required_tool_call": {"name": "get_order_status", "arguments": {"order_id": "10001"}},
                "tool_result_fields": {"found": True, "status": "已发货"},
            }},
            {"message": "它的物流单号是什么？", "expected": {
                "http_status": 200,
                "required_tool_call": {"name": "get_order_status", "arguments": {"order_id": "10001"}},
                "tool_result_fields": {"found": True, "tracking_number": "SF1234567890"},
            }},
        ],
    }


class DialogueTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_turns_share_one_conversation(self):
        inputs = []
        async def offline_response(**kwargs):
            messages = kwargs['messages']
            inputs.append(len(messages))
            question = next(item['content'] for item in reversed(messages) if item['role'] == 'user')
            if messages[-1]['role'] == 'tool':
                data = json.loads(messages[-1]['content'])
                content = data['tracking_number'] if '物流' in question else data['status']
                message = ChatCompletionMessage(role='assistant', content='离线模拟回答：' + content)
            else:
                if '物流' in question:
                    self.assertNotIn('10001', question)
                    self.assertIn('10001', messages[0]['content'])
                message = ChatCompletionMessage(role='assistant', tool_calls=[{
                    'id': f'offline_{len(inputs)}', 'type': 'function',
                    'function': {'name': 'get_order_status', 'arguments': '{"order_id":"10001"}'},
                }])
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(runner.llm_service.client.chat.completions, 'create', new=offline_response):
            report = await runner.collect_dialogue(dialogue_case())
        self.assertEqual(inputs, [2, 4, 4, 6])
        self.assertEqual(len(report['executed_tools']), 2)
        self.assertEqual(len(report['turns']), 2)
        ids = {turn['request']['conversation_id'] for turn in report['turns']}
        self.assertEqual(ids, {report['conversation_id']})
        self.assertTrue(all(report['checks'].values()))
        self.assertEqual(report['task_verdict'], 'pending')

    async def test_failure_stops_later_turns(self):
        async def offline_failure(**kwargs):
            raise TimeoutError('offline only')
        with patch.object(runner.llm_service.client.chat.completions, 'create', new=offline_failure):
            report = await runner.collect_dialogue(dialogue_case())
        self.assertEqual(len(report['turns']), 1)
        self.assertFalse(report['checks']['all_turns_executed'])
        self.assertEqual(report['task_verdict'], 'failed_or_incomplete')
        self.assertIn('后续轮次未执行', report['stop_reason'])

    async def test_optional_followup_uses_previous_tool_evidence(self):
        case = dialogue_case()
        case['case_version'] = 2
        case['turns'][1]['expected']['tool_policy'] = 'optional'
        calls = []
        async def offline_response(**kwargs):
            calls.append(len(kwargs['messages']))
            if len(calls) == 1:
                message = ChatCompletionMessage(role='assistant', tool_calls=[{
                    'id': 'first-call', 'type': 'function',
                    'function': {'name': 'get_order_status', 'arguments': '{"order_id":"10001"}'},
                }])
            else:
                message = ChatCompletionMessage(role='assistant', content='离线模拟：已发货，物流号SF1234567890。')
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(runner.llm_service.client.chat.completions, 'create', new=offline_response):
            report = await runner.collect_dialogue(case)
        self.assertEqual(calls, [2, 4, 4])
        self.assertEqual(len(report['executed_tools']), 1)
        self.assertTrue(report['turns'][1]['checks']['history_evidence_available'])
        self.assertTrue(all(report['checks'].values()))
        self.assertEqual(report['case_version'], 2)
        self.assertEqual(report['task_verdict'], 'pending')

    def test_multiturn_listing(self):
        self.assertIn('它的物流单号是什么？', runner.case_description(dialogue_case()))


if __name__ == '__main__':
    unittest.main()
