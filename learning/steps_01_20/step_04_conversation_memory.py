# 课程：step_04_conversation_memory.md；访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。
"""
第 4 步：使用内存中的消息列表实现多轮对话。

启动方式（在项目根目录下）：
    python -m uvicorn learning.steps_01_20.step_04_conversation_memory:app --reload
"""

from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings


SYSTEM_PROMPT = "你是一名简洁、耐心的学习助手。"


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("conversation_id", "message")
    @classmethod
    def remove_surrounding_spaces(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("内容不能为空")
        return cleaned_value


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    model: str


app = FastAPI(title="第 4 步：多轮对话")
settings = get_settings()
client = AsyncOpenAI(
    max_retries=0,
    timeout=30,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


# key 是会话 ID，value 是这段会话的全部消息。
histories: dict[str, list[dict[str, str]]] = {}


def get_history(conversation_id: str) -> list[dict[str, str]]:
    """获取会话历史；第一次使用某个 ID 时，创建一段新会话。"""
    if conversation_id not in histories:
        histories[conversation_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]
    return histories[conversation_id]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    history = get_history(request.conversation_id)

    # 先记住用户这一轮说的话。
    history.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    try:
        # 每次都把这段会话的全部历史重新发给模型。
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=history,
        )
    except Exception:
        # 如果模型调用失败，删掉本次尚未获得回答的用户消息。
        history.pop()
        raise

    answer = response.choices[0].message.content or "模型没有返回内容"

    # 模型成功回答后，再记住它的回答。
    history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    return ChatResponse(
        conversation_id=request.conversation_id,
        answer=answer,
        model=settings.llm_model,
    )


# 这是学习用接口，方便直接观察内存中保存的会话。
@app.get("/history/{conversation_id}")
async def read_history(conversation_id: str) -> dict[str, object]:
    return {
        "conversation_id": conversation_id,
        "messages": histories.get(conversation_id, []),
    }
