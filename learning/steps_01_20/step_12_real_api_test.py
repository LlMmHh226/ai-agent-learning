# 课程：step_12_real_api_test.md；访问范围：真实外部请求（可能收费）。
"""
第 12 步：直接调用真实大模型 API 的集成测试。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_12_real_api_test -v
"""

import unittest

from app.services.llm_service import LLMService


class RealAPIIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_model_returns_text(self) -> None:
        # Arrange：创建使用 .env 配置的真实模型服务。
        service = LLMService()

        # Act：实际发起网络请求。
        answer = await service.chat(
            "请只用一句简短的话回答：API连接测试成功。"
        )

        # 方便学习时直接观察真实模型返回了什么。
        print(f"\n真实模型回答：{answer}")

        # Assert：真实模型措辞可能变化，所以只检查类型和非空内容。
        self.assertIsInstance(answer, str)
        self.assertTrue(answer.strip())


if __name__ == "__main__":
    unittest.main()
