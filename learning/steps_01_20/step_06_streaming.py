# 课程：step_06_streaming.md；访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。
"""
第 6 步：对比普通回答与流式回答。

启动方式（在项目根目录下）：
    python -m uvicorn learning.steps_01_20.step_06_streaming:app --reload
"""

import logging
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings


logger = logging.getLogger(__name__)
SYSTEM_PROMPT = "你是一名简洁、耐心的学习助手。"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("消息不能为空")
        return cleaned_value


class ChatResponse(BaseModel):
    answer: str


app = FastAPI(title="第 6 步：流式输出")
settings = get_settings()
client = AsyncOpenAI(
    max_retries=0,
    timeout=30,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


def build_messages(message: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]


# 普通接口：等模型生成完整答案后，一次性返回 JSON。
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=build_messages(request.message),
    )
    answer = response.choices[0].message.content
    return ChatResponse(answer=answer or "模型没有返回内容")


async def generate_answer(message: str) -> AsyncGenerator[str, None]:
    """每获得一个有内容的数据块，就立即交给 StreamingResponse。"""
    try:
        stream = await client.chat.completions.create(
            model=settings.llm_model,
            messages=build_messages(message),
            stream=True,
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception:
        logger.exception("流式调用大模型失败")
        yield "\n\nAI 服务暂时不可用，请稍后重试。"


# 流式接口：返回的是异步生成器，而不是一个已完成的答案。
@app.post("/chat/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        content=generate_answer(request.message),
        media_type="text/plain; charset=utf-8",
    )
