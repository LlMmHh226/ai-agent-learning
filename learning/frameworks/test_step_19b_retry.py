"""检查SDK重试配置、正文返回与最终异常传播；不验证SDK内部重试。"""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage

from learning.frameworks import step_19b_langchain_single_call as demo


class HTTPError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code


class RetryTests(unittest.IsolatedAsyncioTestCase):
    async def run_case(self, responses, expected_error=None):
        model = SimpleNamespace(ainvoke=AsyncMock(side_effect=responses))
        settings = SimpleNamespace(
            llm_model="test-model", llm_api_key="test-only", llm_base_url="https://example.invalid"
        )
        with (
            patch.object(demo, "get_settings", return_value=settings),
            patch.object(demo, "ChatOpenAI", return_value=model) as factory,
            patch.object(demo.asyncio, "sleep", new_callable=AsyncMock) as sleep,
            patch("builtins.print"),
        ):
            if expected_error is None:
                answer = await demo.ask_customer_service("你好")
                self.assertEqual(answer, "你好，我是电商客服。")
            else:
                with self.assertRaises(HTTPError) as caught:
                    await demo.ask_customer_service("你好")
                self.assertIs(caught.exception, expected_error)
            self.assertEqual(factory.call_args.kwargs["max_retries"], 0)
        return model.ainvoke, sleep

    async def test_immediate_success(self):
        invoke, sleep = await self.run_case([AIMessage(content="你好，我是电商客服。")])
        self.assertEqual(invoke.await_count, 1)
        sleep.assert_not_awaited()

    async def test_final_429_not_retried_by_outer_code(self):
        error = HTTPError(429)
        invoke, sleep = await self.run_case([error], expected_error=error)
        self.assertEqual(invoke.await_count, 1)
        sleep.assert_not_awaited()

    async def test_other_final_errors_propagate(self):
        for status in (401, 500):
            with self.subTest(status=status):
                error = HTTPError(status)
                invoke, sleep = await self.run_case([error], expected_error=error)
                self.assertEqual(invoke.await_count, 1)
                sleep.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
