"""离线验证采集器：模型响应模拟，正式路由和本地业务执行；不输出效果报告。"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openai.types.chat import ChatCompletionMessage

from learning.evaluation.step_02_run_first_case import ROOT, collect_case, llm_service


class CollectorTests(unittest.IsolatedAsyncioTestCase):
    def load_case(self):
        return json.loads((ROOT / 'learning/evaluation/cases/agent_baseline.json').read_text(encoding='utf-8'))['cases'][0]

    async def test_success_trace_and_pending_semantic_review(self):
        calls = []
        async def offline_response(**kwargs):
            calls.append(len(kwargs['messages']))
            if len(calls) == 1:
                message = ChatCompletionMessage(role='assistant', tool_calls=[{
                    'id': 'offline-test-call', 'type': 'function',
                    'function': {'name': 'get_order_status', 'arguments': '{"order_id":"10001"}'},
                }])
            else:
                data = json.loads(kwargs['messages'][-1]['content'])
                message = ChatCompletionMessage(role='assistant', content='离线模拟回答：' + data['tracking_number'])
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(llm_service.client.chat.completions, 'create', new=offline_response):
            report = await collect_case(self.load_case())
            self.assertIs(llm_service.client.chat.completions.create, offline_response)
        self.assertEqual(calls, [2, 4])
        self.assertTrue(all(report['checks'].values()))
        self.assertEqual(report['human_review']['status'], 'pending')
        self.assertEqual(report['task_verdict'], 'pending')
        self.assertEqual(report['executed_tools'][0]['arguments'], {'order_id': '10001'})

    async def test_failure_is_retained(self):
        async def offline_failure(**kwargs):
            raise TimeoutError('offline test only')
        with patch.object(llm_service.client.chat.completions, 'create', new=offline_failure):
            report = await collect_case(self.load_case())
        self.assertEqual(report['http']['status'], 502)
        self.assertEqual(report['model_calls'][0]['error_type'], 'TimeoutError')
        self.assertEqual(report['task_verdict'], 'failed_or_incomplete')
        self.assertFalse(report['checks']['required_tool_and_arguments'])

    async def test_missing_order_is_a_valid_business_result(self):
        case = self.load_case()
        case['id'] = 'offline_missing_order'
        case['request']['message'] = '请查询订单99999的物流单号。'
        case['expected']['required_tool_call']['arguments'] = {'order_id': '99999'}
        case['expected']['tool_result_fields'] = {'found': False}
        calls = []
        async def offline_response(**kwargs):
            calls.append(len(kwargs['messages']))
            if len(calls) == 1:
                message = ChatCompletionMessage(role='assistant', tool_calls=[{
                    'id': 'offline-missing-call', 'type': 'function',
                    'function': {'name': 'get_order_status', 'arguments': '{"order_id":"99999"}'},
                }])
            else:
                data = json.loads(kwargs['messages'][-1]['content'])
                self.assertIs(data['found'], False)
                message = ChatCompletionMessage(role='assistant', content='离线模拟回答：未找到订单，请核对订单号。')
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(llm_service.client.chat.completions, 'create', new=offline_response):
            report = await collect_case(case)
        self.assertEqual(report['http']['status'], 200)
        self.assertTrue(all(report['checks'].values()))
        self.assertEqual(report['task_verdict'], 'pending')
        self.assertEqual(calls, [2, 4])

    def no_order_id_case(self):
        case = self.load_case()
        case['id'] = 'offline_no_order_id'
        case['request']['message'] = '帮我查一下订单的物流单号。'
        case['expected'].update(tool_policy='none', required_tool_call=None, tool_result_fields={})
        return case

    async def test_no_tool_policy_accepts_clarification(self):
        async def offline_response(**kwargs):
            message = ChatCompletionMessage(role='assistant', content='请提供订单号，以便查询物流信息。')
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(llm_service.client.chat.completions, 'create', new=offline_response):
            report = await collect_case(self.no_order_id_case())
        self.assertTrue(all(report['checks'].values()))
        self.assertEqual(report['executed_tools'], [])
        self.assertEqual(len(report['model_calls']), 1)
        self.assertEqual(report['task_verdict'], 'pending')

    async def test_no_tool_policy_rejects_guessed_order_call(self):
        calls = []
        async def offline_response(**kwargs):
            calls.append(1)
            if len(calls) == 1:
                message = ChatCompletionMessage(role='assistant', tool_calls=[{
                    'id': 'guessed-order', 'type': 'function',
                    'function': {'name': 'get_order_status', 'arguments': '{"order_id":"10001"}'},
                }])
            else:
                message = ChatCompletionMessage(role='assistant', content='请提供订单号。')
            return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
        with patch.object(llm_service.client.chat.completions, 'create', new=offline_response):
            report = await collect_case(self.no_order_id_case())
        self.assertTrue(report['checks']['http_ok'])
        self.assertFalse(report['checks']['no_tool_calls'])
        self.assertEqual(report['task_verdict'], 'failed_or_incomplete')

    async def test_conflicting_no_tool_expectation_rejected_before_run(self):
        case = self.load_case()
        case['expected']['tool_policy'] = 'none'
        with patch.object(llm_service.client.chat.completions, 'create') as create:
            with self.assertRaisesRegex(ValueError, '不调用工具时'):
                await collect_case(case)
            create.assert_not_called()


if __name__ == '__main__':
    unittest.main()
