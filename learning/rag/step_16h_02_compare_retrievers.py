# 课程：step_16h_02_compare_retrievers.md；访问范围：真实外部请求（可能收费）。
from dataclasses import dataclass
from time import perf_counter

from app.rag.chunker import split_documents
from app.rag.dense_retriever import DenseRetriever
from app.rag.document_loader import load_markdown_documents
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.retriever import retrieve
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError
from learning.rag.step_16h_01_ngram_eval_baseline import (
    EVALUATION_CASES,
    RetrievalEvalMetrics,
    evaluate_retriever,
)


@dataclass(frozen=True)
class RetrieverComparison:
    name: str
    k: int
    metrics: RetrievalEvalMetrics


class PrecomputedEmbeddingService:
    """让评测阶段复用两次批量请求已经得到的真实向量。"""

    def __init__(
        self,
        document_vectors_by_text: dict[str, list[float]],
        query_vectors_by_text: dict[str, list[float]],
    ) -> None:
        self.document_vectors_by_text = document_vectors_by_text
        self.query_vectors_by_text = query_vectors_by_text

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [
            list(self.document_vectors_by_text[text])
            for text in texts
        ]

    def embed_query(self, text: str) -> list[float]:
        return list(self.query_vectors_by_text[text])


def main() -> None:
    chunks = split_documents(
        documents=load_markdown_documents(),
        chunk_size=10_000,
        overlap=0,
    )
    questions = [case.question for case in EVALUATION_CASES]
    embedding_service = EmbeddingService()

    try:
        document_start = perf_counter()
        document_vectors = embedding_service.embed_documents(
            [chunk.content for chunk in chunks]
        )
        document_batch_ms = (perf_counter() - document_start) * 1000

        query_start = perf_counter()
        query_vectors = embedding_service.embed_queries(questions)
        query_batch_ms = (perf_counter() - query_start) * 1000
    except EmbeddingServiceError as error:
        print(f"真实 Embedding 评测停止：{error}")
        raise SystemExit(1) from error

    precomputed_service = PrecomputedEmbeddingService(
        document_vectors_by_text={
            chunk.content: vector
            for chunk, vector in zip(chunks, document_vectors)
        },
        query_vectors_by_text={
            question: vector
            for question, vector in zip(questions, query_vectors)
        },
    )
    dense_retriever = DenseRetriever(
        embedding_service=precomputed_service,  # type: ignore[arg-type]
    )
    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
    )

    def retrieve_ngram_sources(question: str, k: int) -> list[str]:
        results = retrieve(
            query=question,
            chunks=chunks,
            top_k=k,
            min_score=0.0,
        )
        return [result.document.metadata["source"] for result in results]

    def retrieve_dense_sources(question: str, k: int) -> list[str]:
        results = dense_retriever.retrieve(
            query=question,
            documents=chunks,
            top_k=k,
        )
        return [result.document.metadata["source"] for result in results]

    def retrieve_hybrid_sources(question: str, k: int) -> list[str]:
        results = hybrid_retriever.retrieve(
            query=question,
            documents=chunks,
            top_k=k,
        )
        return [result.document.metadata["source"] for result in results]

    comparisons: list[RetrieverComparison] = []
    retrievers = [
        ("n-gram", retrieve_ngram_sources),
        ("Dense", retrieve_dense_sources),
        ("Hybrid", retrieve_hybrid_sources),
    ]

    for name, retrieve_sources in retrievers:
        for k in (1, 3):
            metrics = evaluate_retriever(
                cases=EVALUATION_CASES,
                retrieve_sources=retrieve_sources,
                k=k,
            )
            comparisons.append(
                RetrieverComparison(
                    name=name,
                    k=k,
                    metrics=metrics,
                )
            )

    print("\n=== 同一评测集对比 ===")
    for comparison in comparisons:
        metrics = comparison.metrics
        print(
            f"{comparison.name:7} K={comparison.k} "
            f"Recall={metrics.recall_at_k:.1%} "
            f"Precision={metrics.precision_at_k:.1%} "
            f"本地检索平均耗时={metrics.average_latency_ms:.3f}ms"
        )

    print("\n=== 两次真实批量 Embedding 请求 ===")
    print(
        f"document批量：输入={len(chunks)}，耗时={document_batch_ms:.1f}ms"
    )
    print(
        f"query批量：输入={len(questions)}，耗时={query_batch_ms:.1f}ms，"
        f"批量平均={query_batch_ms / len(questions):.1f}ms/问题"
    )


if __name__ == "__main__":
    main()
