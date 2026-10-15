# 课程：step_16_tool_selection_eval.md；访问范围：真实外部请求（可能收费）。
"""
第 16 步：使用真实模型评测工具选择。

运行方式（在项目根目录下）：
    python -m learning.steps_01_20.step_16_tool_selection_eval
"""

import asyncio
from dataclasses import dataclass

from openai import APIError, AsyncOpenAI

from app.core.config import get_settings
from app.services.llm_service import AVAILABLE_TOOLS, DEFAULT_SYSTEM_PROMPT


@dataclass
class EvalCase:
    question: str
    expected_tool: str | None


CASES = [
    EvalCase("帮我看看10001这个单子到哪里了", "get_order_status"),
    EvalCase("订单10002怎么还没发货？", "get_order_status"),
    EvalCase("东西不想要了，签收后几天内能退？", "get_after_sales_policy"),
    EvalCase("退货通过以后，钱什么时候能到账？", "get_after_sales_policy"),
    EvalCase("你好，请介绍一下你自己", None),
]


async def select_tool(
    client: AsyncOpenAI,
    model: str,
    question: str,
) -> tuple[str | None, str]:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": DEFAULT_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        tools=AVAILABLE_TOOLS,
        tool_choice="auto",
    )

    message = response.choices[0].message
    if not message.tool_calls:
        return None, "-"

    first_call = message.tool_calls[0]
    return first_call.function.name, first_call.function.arguments


async def main() -> None:
    settings = get_settings()
    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        max_retries=0,
        timeout=20.0,
    )

    passed = 0
    completed = 0

    for index, case in enumerate(CASES, start=1):
        try:
            actual_tool, arguments = await select_tool(
                client=client,
                model=settings.llm_model,
                question=case.question,
            )
        except APIError as error:
            status_code = getattr(error, "status_code", None)
            print(f"\n用例 {index}：跳过")
            print(f"用户问题：{case.question}")
            print(f"API 错误：{status_code or type(error).__name__}")
            continue

        completed += 1
        success = actual_tool == case.expected_tool
        passed += int(success)

        print(f"\n用例 {index}：{'通过' if success else '失败'}")
        print(f"用户问题：{case.question}")
        print(f"预期工具：{case.expected_tool or '不调用工具'}")
        print(f"实际工具：{actual_tool or '不调用工具'}")
        print(f"工具参数：{arguments}")

        # 减少服务的短时间请求压力。
        await asyncio.sleep(2)

    if completed:
        accuracy = passed / completed
        print(f"\n已完成用例正确率：{passed}/{completed} = {accuracy:.0%}")
    else:
        print("\n本次没有用例完成，请稍后重试。")


if __name__ == "__main__":
    asyncio.run(main())


