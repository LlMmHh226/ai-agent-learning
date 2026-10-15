from dataclasses import dataclass

from app.rag.dense_retriever import DenseRetriever
from app.rag.document_loader import Document
from app.rag.retriever import retrieve as retrieve_ngram


DEFAULT_RRF_K = 60


@dataclass
class HybridRetrievalResult:
    document: Document
    score: float


class HybridRetriever:
    """使用 RRF 合并 n-gram 与 Dense 的候选排名。"""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        rrf_k: int = DEFAULT_RRF_K,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError("rrf_k 必须大于 0")

        self.dense_retriever = dense_retriever
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 3,
    ) -> list[HybridRetrievalResult]:
        """分别召回两路候选，使用 RRF 分数合并后返回 Top-K。"""
        if not query.strip():
            raise ValueError("query 不能为空字符串")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if not documents:
            return []

        candidate_k = min(len(documents), top_k * 2)
        ngram_results = retrieve_ngram(
            query=query,
            chunks=documents,
            top_k=candidate_k,
            min_score=0.0,
        )
        dense_results = self.dense_retriever.retrieve(
            query=query,
            documents=documents,
            top_k=candidate_k,
        )

        documents_by_key: dict[tuple[str, str], Document] = {}
        scores_by_key: dict[tuple[str, str], float] = {}

        for rank, result in enumerate(ngram_results, start=1):
            key = self._document_key(result.document)
            documents_by_key[key] = result.document
            scores_by_key[key] = scores_by_key.get(key, 0.0) + self._rrf_score(
                rank
            )

        for rank, result in enumerate(dense_results, start=1):
            key = self._document_key(result.document)
            documents_by_key[key] = result.document
            scores_by_key[key] = scores_by_key.get(key, 0.0) + self._rrf_score(
                rank
            )

        results = [
            HybridRetrievalResult(
                document=documents_by_key[key],
                score=score,
            )
            for key, score in scores_by_key.items()
        ]
        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )
        return results[:top_k]

    def _rrf_score(self, rank: int) -> float:
        return 1.0 / (self.rrf_k + rank)

    @staticmethod
    def _document_key(document: Document) -> tuple[str, str]:
        return (
            document.metadata.get("source", ""),
            document.content,
        )
