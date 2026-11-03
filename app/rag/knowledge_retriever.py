"""正式RAG和Agent工具共用的检索入口；支持显式切回历史n-gram实现。"""

from functools import lru_cache

from app.core.config import get_settings
from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.rag.pgvector_retriever import PgvectorRetriever
from app.rag.retriever import RetrievalResult, retrieve
from app.repositories.knowledge_repository import KnowledgeRepositoryError
from app.services.embedding_service import EmbeddingServiceError


class KnowledgeRetrievalError(RuntimeError):
    """检索失败，不能将其作为无相关资料或静默切换检索方式。"""


@lru_cache
def load_local_chunks(chunk_size: int = 10_000) -> list[Document]:
    return split_documents(load_markdown_documents(), chunk_size=chunk_size, overlap=0)


def retrieve_knowledge(
    query: str,
    *,
    backend: str | None = None,
    top_k: int | None = None,
    min_score: float | None = None,
    chunks: list[Document] | None = None,
) -> list[RetrievalResult]:
    settings = get_settings()
    backend = backend if backend is not None else settings.knowledge_retrieval_backend
    if backend == "ngram":
        return retrieve(
            query=query,
            chunks=chunks if chunks is not None else load_local_chunks(),
            top_k=top_k if top_k is not None else 1,
            min_score=min_score if min_score is not None else 0.3,
        )
    if backend != "pgvector":
        raise ValueError("不支持的知识库检索后端")
    try:
        return PgvectorRetriever().retrieve(
            query=query,
            top_k=top_k if top_k is not None else settings.pgvector_top_k,
            min_score=min_score if min_score is not None else settings.pgvector_min_score,
        )
    except (EmbeddingServiceError, KnowledgeRepositoryError, ValueError) as error:
        # 对调用者保留服务故障语义，不把供应商异常详情或凭据写进响应。
        raise KnowledgeRetrievalError(
            "知识库检索暂时不可用（" + type(error).__name__ + "）。"
        ) from None
