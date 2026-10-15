# 课程：step_16_check_embedding_support.md；访问范围：真实外部请求（可能收费）。
import asyncio

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from app.core.config import get_settings


EMBEDDING_NAME_HINTS = (
    "embedding",
    "embed",
    "bge",
    "e5",
    "gte",
    "jina",
)


async def check_embedding_candidates() -> None:
    """
    从当前 OpenAI 兼容服务的模型列表中筛选 Embedding 候选。

    参数:
        无。函数通过 get_settings() 读取项目已有配置，但不会打印
        API Key。

    返回:
        无业务返回值。函数只打印模型总数、候选名称或错误状态。
    """
    settings = get_settings()
    client = AsyncOpenAI(
        max_retries=0,
        timeout=30,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )

    try:
        model_page = await client.models.list()
        model_ids = [model.id for model in model_page.data]
        candidates = [
            model_id
            for model_id in model_ids
            if any(
                hint in model_id.lower()
                for hint in EMBEDDING_NAME_HINTS
            )
        ]

        print(f"服务返回模型数量：{len(model_ids)}")
        print(f"名称疑似 Embedding 的候选：{candidates}")
        if not candidates:
            print(
                "模型列表中未发现明显候选；这不能单独证明服务不支持，"
                "还需要服务方文档或明确模型名。"
            )
    except RateLimitError:
        print("模型服务返回 429，未重复调用。")
    except APIStatusError as error:
        print(f"模型列表接口返回 HTTP {error.status_code}。")
    except APIConnectionError:
        print("无法连接当前模型服务。")
    finally:
        await client.close()


asyncio.run(check_embedding_candidates())
