# 课程：step_02_fastapi_chat.md；访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。
"""
第 2 步：把一次大模型对话变成 HTTP 接口。

启动方式（在项目根目录下）：
    python -m uvicorn learning.steps_01_20.step_02_fastapi_chat:app --reload
"""

from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings


# 1. 定义客户端发来的 JSON 结构。
class ChatRequest(BaseModel):
    message: str



# 2. 定义服务器返回的 JSON 结构。
class ChatResponse(BaseModel):
    answer: str
    model: str


# 3. 创建 FastAPI 应用和大模型客户端。
app = FastAPI(title="第 2 步：最小聊天接口")
settings = get_settings()
client = AsyncOpenAI(
    max_retries=0,
    timeout=30,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


# 4. 客户端 POST /chat 时，FastAPI 会调用这个函数。
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

@app.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest) -> ChatResponse:
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "你是一名python入门老师。",
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
