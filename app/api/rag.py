import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest
from app.schemas.rag import RAGChatResponse, RAGSourceResponse
from app.services.rag_service import rag_service


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


@router.post("/chat", response_model=RAGChatResponse)
async def rag_chat(request: ChatRequest) -> RAGChatResponse:
    """
    接收一个经过校验的用户问题，并返回 RAG 回答和来源。

    参数:
        request:
            FastAPI 根据请求 JSON 创建的 ChatRequest。它复用现有
            message 的去空格、非空和最大长度校验。

    返回:
        RAGChatResponse。answer 来自 RAGService，sources 由 Python
        根据真实检索结果转换为响应模型。
    """
    try:
        result = await rag_service.chat(query=request.message)
        return RAGChatResponse(
            answer=result.answer,
            sources=[
                RAGSourceResponse(
                    source=source.source,
                    chunk_id=source.chunk_id,
                    snippet=source.snippet,
                )
                for source in result.sources
            ],
        )
    except Exception:
        logger.exception("RAG 调用失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 服务暂时不可用，请稍后重试",
        )
