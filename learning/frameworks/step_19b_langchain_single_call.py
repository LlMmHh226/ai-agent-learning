# 课程：step_19b_langchain_single_call.md；访问范围：真实外部请求（可能收费）。
"""19B：一次真实LangChain调用，观察消息对象和函数返回值。"""

import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings


async def ask_customer_service(question: str) -> str:
    """发送一个问题，返回纯文本回答。

    参数：question是main传入的用户问题字符串，用于HumanMessage正文。
    返回：reply.content中的字符串，交给main里的answer；非文本则报错。
    """
    settings = get_settings()
    model = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=30,
        max_retries=0,
    )
    messages = [
        SystemMessage(content="你是一名电商客服，请用一句简短的中文问候回答。"),
        HumanMessage(content=question),
    ]
    print("question：", question)
    print("messages类型：", [type(message).__name__ for message in messages])
    print("开始请求模型，本示例不自动重试……")
    reply = await model.ainvoke(messages)
    print("reply类型：", type(reply).__name__)
    print("reply.content类型：", type(reply.content).__name__)
    if not isinstance(reply.content, str) or not reply.content.strip():
        raise ValueError("本步预期非空文本回答，实际输出不符合要求。")
    return reply.content


async def main() -> None:
    """学习入口，无参数；打印接收到的answer，返回None。"""
    try:
        answer = await ask_customer_service(question="你好")
    except Exception as error:
        # 不打印异常正文、请求对象或配置，以免供应商错误携带敏感信息。
        print("调用未完成，异常类型：", type(error).__name__)
        status_code = getattr(error, "status_code", None)
        if isinstance(status_code, int):
            print("HTTP状态码：", status_code)
        print("调用失败：请求失败，本示例不自动重试。")
        raise SystemExit(1) from None
    print("main里的answer：", answer)


if __name__ == "__main__":
    asyncio.run(main())
