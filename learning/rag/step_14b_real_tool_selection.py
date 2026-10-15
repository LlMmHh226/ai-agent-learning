# 课程：step_14b_real_tool_selection.md；访问范围：真实外部请求（可能收费）。
import asyncio

from openai import RateLimitError

from app.services.llm_service import (
    AVAILABLE_TOOLS,
    DEFAULT_SYSTEM_PROMPT,
    llm_service,
)


query = "星云机械键盘支持热插拔吗？"
messages = [
    {
        "role": "system",
        "content": DEFAULT_SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": query,
    },
]

try:
    response = asyncio.run(
        llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=messages,
            tools=AVAILABLE_TOOLS,
            tool_choice="auto",
        )
    )
    assistant_message = response.choices[0].message

    print(f"用户问题：{query}")
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            print(f"模型选择工具：{tool_call.function.name}")
            print(f"模型生成参数：{tool_call.function.arguments}")
    else:
        print("模型没有选择工具。")
        print(f"模型直接回答：{assistant_message.content}")
except RateLimitError:
    print("模型服务返回 429 限流，本次不再重复调用，请稍后重试。")
