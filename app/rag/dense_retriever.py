import math
from dataclasses import dataclass

from app.rag.document_loader import Document
from app.rag.embedding_cache import KnowledgeEmbeddingCache
from app.services.embedding_service import EmbeddingService


@dataclass
class DenseRetrievalResult:
    document: Document
    score: float


def calculate_cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """使用两个完整且等长的向量计算余弦相似度。"""
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须相同")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("不能计算零向量的余弦相似度")

    return dot_product / (magnitude_a * magnitude_b)


class DenseRetriever:
    """使用 Embedding 余弦相似度对知识文档进行 Top-K 检索。"""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self.embedding_cache = KnowledgeEmbeddingCache(
            embedding_service=embedding_service,
        )

    def retrieve(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 3,
    ) -> list[DenseRetrievalResult]:
        """返回与 query 余弦相似度最高的前 top_k 篇文档。"""
        if not query.strip():
            raise ValueError("query 不能为空字符串")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if not documents:
            return []

        embedded_documents = self.embedding_cache.get_embeddings(documents)
        query_vector = self.embedding_service.embed_query(query)

        results = [
            DenseRetrievalResult(
                document=embedded_document.document,
                score=calculate_cosine_similarity(
                    vector_a=query_vector,
                    vector_b=embedded_document.vector,
                ),
            )
            for embedded_document in embedded_documents
        ]
        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )
        return results[:top_k]
