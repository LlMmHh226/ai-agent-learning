from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户消息",
        examples=["你好"],
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("消息不能为空")
        return value


class ChatResponse(BaseModel):
    answer: str
    model: str


class ConversationChatRequest(ChatRequest):
    conversation_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="会话ID",
        examples=["conversation-001"],
    )


class ConversationChatResponse(ChatResponse):
    conversation_id: str
