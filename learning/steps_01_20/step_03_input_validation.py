# 课程：step_03_input_validation.md；访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。
"""
第 3 步：为聊天接口增加输入校验。

启动方式（在项目根目录下）：
    python -m uvicorn learning.steps_01_20.step_03_input_validation:app --reload
"""

from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings


class ChatRequest(BaseModel):
    # Field 先校验长度，并为 API 文档提供字段说明。
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户发送的聊天消息",
        examples=["用一句话解释什么是 API"],
    )

    # 长度校验拦不住“   ”，所以去掉首尾空格后再检查。
    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("消息不能为空")
        return cleaned_value


class ChatResponse(BaseModel):
    answer: str
    model: str


app = FastAPI(title="第 3 步：带输入校验的聊天接口")
settings = get_settings()
client = AsyncOpenAI(
    max_retries=0,
    timeout=30,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "你是一名简洁、耐心的学习助手。",
            },
            {
                "role": "user",
                "content": request.message,
            },
        ],
    )

    answer = response.choices[0].message.content
    return ChatResponse(
        answer=answer or "模型没有返回内容",
        model=settings.llm_model,
    )
