"""只核对规则语义，不请求模型或HTTP。"""

import unittest
from copy import deepcopy

from learning.evaluation.step_02_run_first_case import check_tool_policy


class OptionalPolicyTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            'tool_policy': 'optional',
            'required_tool_call': {'name': 'get_order_status', 'arguments': {'order_id': '10001'}},
            'tool_result_fields': {'found': True, 'order_id': '10001', 'tracking_number': 'SF1234567890'},
        }
        self.evidence = {
            'name': 'get_order_status', 'arguments': {'order_id': '10001'},
            'result': {'found': True, 'order_id': '10001', 'tracking_number': 'SF1234567890'},
        }
        self.model_calls = [{'status': 'completed', 'proposed_tools': []}]

    def test_no_call_requires_prior_matching_evidence(self):
        checks = check_tool_policy(self.expected, self.model_calls, [], [self.evidence])
        self.assertTrue(checks['history_evidence_available'])
        self.assertFalse(check_tool_policy(self.expected, self.model_calls, [])['history_evidence_available'])

    def test_wrong_order_history_does_not_count(self):
        wrong = deepcopy(self.evidence)
        wrong['arguments']['order_id'] = '10002'
        self.assertFalse(check_tool_policy(self.expected, self.model_calls, [], [wrong])['history_evidence_available'])

    def test_valid_requery_allowed(self):
        proposal = {'name': self.evidence['name'], 'arguments': self.evidence['arguments']}
        calls = [{'status': 'completed', 'proposed_tools': [proposal]}]
        self.assertTrue(check_tool_policy(self.expected, calls, [self.evidence])['optional_tool_calls_valid'])

    def test_wrong_requery_cannot_hide_behind_valid_history(self):
        wrong = deepcopy(self.evidence)
        wrong['arguments']['order_id'] = '10002'
        calls = [{'status': 'completed', 'proposed_tools': [wrong]}]
        self.assertFalse(check_tool_policy(self.expected, calls, [wrong], [self.evidence])['optional_tool_calls_valid'])

    def test_incomplete_model_call_not_evidence(self):
        checks = check_tool_policy(self.expected, [{'status': 'error'}], [], [self.evidence])
        self.assertFalse(checks['history_evidence_available'])

    def test_current_result_must_match_facts(self):
        wrong = deepcopy(self.evidence)
        wrong['result']['tracking_number'] = 'WRONG'
        calls = [{'status': 'completed', 'proposed_tools': [wrong]}]
        self.assertFalse(check_tool_policy(self.expected, calls, [wrong])['optional_tool_calls_valid'])

    def test_newer_result_supersedes_older_evidence(self):
        changed = deepcopy(self.evidence)
        changed['result']['tracking_number'] = 'UPDATED'
        checks = check_tool_policy(self.expected, self.model_calls, [], [self.evidence, changed])
        self.assertFalse(checks['history_evidence_available'])


if __name__ == '__main__':
    unittest.main()
