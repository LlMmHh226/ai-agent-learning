import asyncio
from dataclasses import dataclass

from app.core.config import get_settings
from app.rag.document_loader import Document, load_markdown_documents
from app.rag.chunker import split_documents
from app.rag.knowledge_retriever import retrieve_knowledge
from app.rag.prompt_builder import (
    RAG_INSUFFICIENT_CONTEXT_RESPONSE,
    build_rag_messages,
)
from app.rag.retriever import RetrievalResult
from app.services.llm_service import llm_service


DOCUMENT_LEVEL_CHUNK_SIZE = 10_000
DEFAULT_RAG_TOP_K = 1
DEFAULT_RAG_MIN_SCORE = 0.3


@dataclass
class RAGSource:
    source: str
    chunk_id: str
    snippet: str


@dataclass
class RAGResult:
    answer: str
    sources: list[RAGSource]


def build_sources(
    retrieval_results: list[RetrievalResult],
) -> list[RAGSource]:
    """
    根据真实检索结果构建可返回给用户的来源列表。

    参数:
        retrieval_results:
            retrieve() 返回的 RetrievalResult 列表。每项都包含命中的
            Document、source、chunk_id 和正文。

    返回:
        RAGSource 列表。每项包含来源文件名、chunk_id 和命中正文；
        返回值会保存到 RAGResult.sources。
    """
    sources: list[RAGSource] = []

    for result in retrieval_results:
        sources.append(
            RAGSource(
                source=result.document.metadata["source"],
                chunk_id=result.document.metadata["chunk_id"],
                snippet=result.document.content,
            )
        )

    return sources


class RAGService:
    def __init__(
        self,
        top_k: int | None = None,
        min_score: float | None = None,
        chunk_size: int = DOCUMENT_LEVEL_CHUNK_SIZE,
        backend: str | None = None,
    ) -> None:
        """
        初始化 RAG 服务；默认从配置选择检索后端，查询时才访问资料。

        参数:
            top_k:
                每次检索最多返回的知识片段数量。未指定时，n-gram使用1，
                pgvector使用配置的PGVECTOR_TOP_K。

            min_score:
                最低相关度。未指定时，n-gram使用0.3，pgvector使用配置的
                PGVECTOR_MIN_SCORE。无命中时直接固定拒答，不调用聊天模型。

            chunk_size:
                n-gram本地模式的片段字符数。pgvector直接使用库中已保存的片段。

        返回:
            保存检索配置；本地片段在需要时才加载，pgvector不读取Markdown。
        """
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if min_score is not None and not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score 必须在 0.0 到 1.0 之间")
        if backend is not None and backend not in {"ngram", "pgvector"}:
            raise ValueError("不支持的知识库检索后端")
        settings = get_settings()
        self._chunks: list[Document] | None = None
        self.chunk_size = chunk_size
        self.backend = backend or settings.knowledge_retrieval_backend
        self.top_k = top_k if top_k is not None else (
            settings.pgvector_top_k if self.backend == "pgvector" else DEFAULT_RAG_TOP_K
        )
        self.min_score = min_score if min_score is not None else (
            settings.pgvector_min_score if self.backend == "pgvector" else DEFAULT_RAG_MIN_SCORE
        )

    @property
    def chunks(self) -> list[Document]:
        """保留历史学习材料的本地片段入口；pgvector路径不依赖Markdown文件。"""
        if self._chunks is None:
            self._chunks = split_documents(
                documents=load_markdown_documents(),
                chunk_size=self.chunk_size,
                overlap=0,
            )
        return self._chunks

    def _retrieve(self, query: str) -> list[RetrievalResult]:
        backend = self.backend
        return retrieve_knowledge(
            query=query,
            backend=backend,
            top_k=self.top_k,
            min_score=self.min_score,
            chunks=self.chunks if backend == "ngram" else None,
        )

    async def chat(self, query: str) -> RAGResult:
        """
        从配置的知识库后端检索，并让模型根据检索正文生成回答。

        参数:
            query:
                用户问题；HTTP接口传入经过校验的request.message。

        返回:
            RAGResult 对象。answer 保存模型回答或固定拒答，sources
            保存 Python 根据检索结果构建的真实来源列表。
        """
        # Embedding SDK和psycopg均为同步调用，避免阻塞FastAPI事件循环。
        retrieval_results = await asyncio.to_thread(self._retrieve, query)
        if not retrieval_results:
            return RAGResult(
                answer=RAG_INSUFFICIENT_CONTEXT_RESPONSE,
                sources=[],
            )

        messages = build_rag_messages(
            query=query,
            retrieval_results=retrieval_results,
        )
        answer = await llm_service.complete_messages(messages=messages)
        sources = build_sources(retrieval_results=retrieval_results)
        return RAGResult(
            answer=answer,
            sources=sources,
        )


rag_service = RAGService()
