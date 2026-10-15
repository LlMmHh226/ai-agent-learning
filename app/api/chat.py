import logging
from fastapi import APIRouter, HTTPException,status
from app.schemas.chat import ChatRequest,ChatResponse,ConversationChatRequest,ConversationChatResponse
from app.services.llm_service import llm_service
from fastapi.responses import StreamingResponse
from app.services.conversation_service import conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["聊天"],
)

@router.post("",response_model=ChatResponse)
async def chat(request: ChatRequest)->ChatResponse:
    try:
        answer = await llm_service.chat(request.message)
        return ChatResponse(answer=answer,model=llm_service.model)
    except Exception:
        logger.exception("调用大模型失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="请稍后重试",
        )

@router.post("/stream")
async def stream(request: ChatRequest)->StreamingResponse:
    return StreamingResponse(
        content=llm_service.stream_chat(request.message),
        media_type="text/plain; charset=utf-8",
    )

@router.post("/conversation",response_model=ConversationChatResponse)
# response_model是什么？
async def conversation_chat(
        request:ConversationChatRequest,
)->ConversationChatResponse:
    try:
        answer=await conversation_service.chat(
            conversation_id=request.conversation_id,
            message=request.message
        )
        return ConversationChatResponse(
            conversation_id=request.conversation_id,
            answer=answer,
            model=llm_service.model
        )
    except Exception:
        logger.exception("多轮对话调用失败")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 服务暂时不可用，请稍后重试",
        )

@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str) -> dict[str, bool]:
    cleared = conversation_service.clear(conversation_id)
    return {
        "cleared": cleared,
    }

