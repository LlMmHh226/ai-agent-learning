# 课程：step_01_basic_chat.md；访问范围：真实外部请求（可能收费）。
"""
第 1 步：用最少的代码完成一次大模型对话。

运行方式（在项目根目录下）：
    python -m learning.steps_01_20.step_01_basic_chat
"""

import asyncio

from openai import AsyncOpenAI

from app.core.config import get_settings
from scripts.check_config import main as check_config


async def main() -> None:
    # 1. 从 .env 中读取 API Key、服务地址和模型名称。
    check_config()
    settings = get_settings()

    # 2. 创建一个用来访问大模型的客户端。
    client = AsyncOpenAI(
        max_retries=0,
        timeout=30,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )

    # 3. 把消息发给模型，并等待完整回答。
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "你是一名简洁、耐心的学习助手。",
            },
            {
                "role": "user",
                "content": "用一句话解释什么是 API。",
            },
        ],
    )

    # 4. 取出模型的第一条回答并打印。
    answer = response.choices[0].message.content
    print(answer)
    await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:
        # 不回显异常正文或配置，供应商错误可能携带请求信息。
        print(f"请求未完成：{type(error).__name__}，HTTP状态：{getattr(error, 'status_code', None)}")
        print("401/403检查权限；429停止并等待额度恢复；连接失败检查地址和网络。详见docs/setup.md。")
        raise SystemExit(1) from None
