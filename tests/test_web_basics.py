"""Web补课应用的输入、响应过滤与业务/服务故障边界。"""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from learning.web_basics.step_01_hello import app


class WebBasicsTests(unittest.TestCase):
    def test_body_validation_and_response_filter(self):
        with TestClient(app) as client:
            self.assertEqual(client.post('/greetings', json={'name':'小明'}).json(), {'message':'你好，小明！'})
            self.assertEqual(client.post('/greetings', json={}).status_code, 422)

    def test_checked_order_distinguishes_invalid_and_missing(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/checked-orders/10001').status_code, 200)
            self.assertEqual(client.get('/checked-orders/abc').status_code, 422)
            self.assertEqual(client.get('/checked-orders/99999').status_code, 404)

    @patch('learning.web_basics.step_01_hello.get_order_status', return_value={'error':'service unavailable'})
    def test_storage_failure_is_service_error_not_missing(self, lookup):
        with TestClient(app) as client:
            self.assertEqual(client.get('/checked-orders/10001').status_code, 503)
