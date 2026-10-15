# 课程：step_08_rag_service.md；访问范围：真实外部请求（可能收费）。
import asyncio

from openai import RateLimitError

from app.services.rag_service import rag_service


query = "物流轨迹超过 48 小时没有更新怎么办？"

try:
    result = asyncio.run(rag_service.chat(query=query))
    print(f"用户问题：{query}")
    print(f"模型回答：{result.answer}")
    print(f"来源数量：{len(result.sources)}")
except RateLimitError:
    print("模型服务返回 429 限流，本次不再重复调用，请稍后重试。")
