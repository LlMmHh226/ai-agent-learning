from dataclasses import dataclass

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.rag.prompt_builder import (
    RAG_INSUFFICIENT_CONTEXT_RESPONSE,
    build_rag_messages,
)
from app.rag.retriever import RetrievalResult, retrieve
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
        top_k: int = DEFAULT_RAG_TOP_K,
        min_score: float = DEFAULT_RAG_MIN_SCORE,
        chunk_size: int = DOCUMENT_LEVEL_CHUNK_SIZE,
    ) -> None:
        """
        初始化 RAG 服务并预先加载本地知识库。

        参数:
            top_k:
                每次检索最多返回的知识片段数量。默认值 1 表示只把
                得分最高的一个结果交给模型。

            min_score:
                检索结果需要达到的最低相关度。当前默认值 0.3；低于
                该分数时，Python 会直接返回固定拒答，不调用模型。

            chunk_size:
                每个知识片段允许的最大字符数。当前默认值 10000，
                使每个短 Markdown 文件形成一个文档级 chunk。

        返回:
            __init__ 不返回业务数据。它把切分结果保存到 self.chunks，
            供后续 chat() 调用重复使用。
        """
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score 必须在 0.0 到 1.0 之间")

        documents = load_markdown_documents()
        self.chunks: list[Document] = split_documents(
            documents=documents,
            chunk_size=chunk_size,
            overlap=0,
        )
        self.top_k = top_k
        self.min_score = min_score

    async def chat(self, query: str) -> RAGResult:
        """
        检索本地知识库，并让模型根据检索上下文生成回答。

        参数:
            query:
                用户问题。学习脚本直接传入字符串；HTTP 接口从
                经过校验的请求 message 中取得该值。

        返回:
            RAGResult 对象。answer 保存模型回答或固定拒答，sources
            保存 Python 根据检索结果构建的真实来源列表。
        """
        retrieval_results = retrieve(
            query=query,
            chunks=self.chunks,
            top_k=self.top_k,
            min_score=self.min_score,
        )
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
