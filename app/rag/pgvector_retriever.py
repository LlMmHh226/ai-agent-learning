"""生成问题向量，由pgvector完成距离排序，返回现有RAG结果结构。"""

import math

from app.rag.document_loader import Document
from app.rag.retriever import RetrievalResult
from app.repositories.knowledge_repository import (
    VECTOR_DIMENSIONS,
    search_knowledge_chunks,
)
from app.services.embedding_service import EmbeddingService


class PgvectorRetriever:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service

    def retrieve(
        self, query: str, top_k: int = 3, min_score: float = 0.5,
    ) -> list[RetrievalResult]:
        if not 1 <= top_k <= 20:
            raise ValueError("top_k 必须在1到20之间")
        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score 必须在0到1之间")
        query = query.strip()
        if not query:
            return []

        service = self.embedding_service or EmbeddingService()
        if service.model != "text-embedding-v4" or service.dimensions != VECTOR_DIMENSIONS:
            raise ValueError("当前知识表使用V4/1536，问题向量必须使用相同配置")
        query_vector = service.embed_query(query)
        rows = search_knowledge_chunks(query_vector, top_k)
        results = []
        for row in rows:
            distance = float(row["distance"])
            if not math.isfinite(distance) or not -1e-6 <= distance <= 2.000001:
                raise ValueError("知识库返回了无效余弦距离")
            score = max(-1.0, min(1.0, 1.0 - distance))
            if score > 0 and score >= min_score:
                results.append(RetrievalResult(
                    document=Document(
                        content=row["content"],
                        metadata={"source": row["source"], "chunk_id": row["chunk_id"]},
                    ),
                    score=score,
                ))
        return results
