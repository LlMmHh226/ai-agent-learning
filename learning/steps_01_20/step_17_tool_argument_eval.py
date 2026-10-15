# 课程：step_17_tool_argument_eval.md；访问范围：真实外部请求（可能收费）。
"""
第 17 步：同时评测工具名称和工具参数。

运行方式（在项目根目录下）：
    python -m learning.steps_01_20.step_17_tool_argument_eval
"""

import asyncio
import json
from dataclasses import dataclass

from openai import APIError, AsyncOpenAI

from app.core.config import get_settings
from learning.steps_01_20.step_16_tool_selection_eval import select_tool


@dataclass
class ArgumentEvalCase:
    question: str
    expected_tool: str
    expected_arguments: dict[str, str]


CASES = [
    ArgumentEvalCase(
        question="请查看订单10003",
        expected_tool="get_order_status",
        expected_arguments={"order_id": "10003"},
    ),
    ArgumentEvalCase(
        question="商品签收以后几天内能退？",
        expected_tool="get_after_sales_policy",
        expected_arguments={"topic": "退货"},
    ),
    ArgumentEvalCase(
        question="退货验收通过后，退款多久能到账？",
        expected_tool="get_after_sales_policy",
        expected_arguments={"topic": "退款"},
    ),
]


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
            actual_tool, arguments_text = await select_tool(
                client=client,
                model=settings.llm_model,
                question=case.question,
            )
        except APIError as error:
            print(f"\n用例 {index}：跳过（API错误 {error.status_code}）")
            continue

        completed += 1

        try:
            actual_arguments = json.loads(arguments_text)
        except json.JSONDecodeError:
            actual_arguments = {}

        tool_correct = actual_tool == case.expected_tool
        arguments_correct = actual_arguments == case.expected_arguments
        success = tool_correct and arguments_correct
        passed += int(success)

        print(f"\n用例 {index}：{'通过' if success else '失败'}")
        print(f"用户问题：{case.question}")
        print(f"工具正确：{tool_correct}")
        print(f"参数正确：{arguments_correct}")
        print(f"预期：{case.expected_tool} {case.expected_arguments}")
        print(f"实际：{actual_tool} {actual_arguments}")

        await asyncio.sleep(2)

    if completed:
        accuracy = passed / completed
        print(f"\n工具及参数正确率：{passed}/{completed} = {accuracy:.0%}")
    else:
        print("\n本次没有用例完成，请稍后重试。")


if __name__ == "__main__":
    asyncio.run(main())
