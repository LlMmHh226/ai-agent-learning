# 课程：step_16h_01_eval_dataset_and_ngram_baseline.md；访问范围：本地运行（无外部模型请求）。
from collections.abc import Callable
from dataclasses import dataclass
from statistics import mean
from time import perf_counter

from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import retrieve


@dataclass(frozen=True)
class RetrievalEvalCase:
    question: str
    expected_source: str


@dataclass(frozen=True)
class RetrievalEvalMetrics:
    recall_at_k: float
    precision_at_k: float
    average_latency_ms: float


EVALUATION_CASES = [
    RetrievalEvalCase("键盘支持蓝牙吗？", "products.md"),
    RetrievalEvalCase("鼠标续航多久？", "products.md"),
    RetrievalEvalCase("物流超过48小时没更新怎么办？", "shipping.md"),
    RetrievalEvalCase("质量问题换货运费谁承担？", "after_sales.md"),
    RetrievalEvalCase("退款多久？", "after_sales.md"),
    RetrievalEvalCase("购买商品什么时候寄出？", "shipping.md"),
    RetrievalEvalCase("快递两天没动静怎么办？", "shipping.md"),
]


def evaluate_retriever(
    cases: list[RetrievalEvalCase],
    retrieve_sources: Callable[[str, int], list[str]],
    k: int,
) -> RetrievalEvalMetrics:
    """使用统一评测集计算 Recall、微平均 Precision 和平均耗时。"""
    if not cases:
        raise ValueError("评测用例不能为空")
    if k <= 0:
        raise ValueError("k 必须大于 0")

    hit_count = 0
    returned_result_count = 0
    latencies_ms: list[float] = []

    for case in cases:
        start_time = perf_counter()
        returned_sources = retrieve_sources(case.question, k)
        elapsed_ms = (perf_counter() - start_time) * 1000
        latencies_ms.append(elapsed_ms)

        hit = case.expected_source in returned_sources
        if hit:
            hit_count += 1
        returned_result_count += len(returned_sources)

        print(
            f"K={k} 命中={hit!s:5} "
            f"预期={case.expected_source:14} "
            f"返回={returned_sources} "
            f"耗时={elapsed_ms:.3f}ms "
            f"问题={case.question}"
        )

    recall_at_k = hit_count / len(cases)
    precision_at_k = (
        hit_count / returned_result_count
        if returned_result_count > 0
        else 0.0
    )

    return RetrievalEvalMetrics(
        recall_at_k=recall_at_k,
        precision_at_k=precision_at_k,
        average_latency_ms=mean(latencies_ms),
    )


def main() -> None:
    chunks = split_documents(
        documents=load_markdown_documents(),
        chunk_size=10_000,
        overlap=0,
    )

    def retrieve_ngram_sources(question: str, k: int) -> list[str]:
        results = retrieve(
            query=question,
            chunks=chunks,
            top_k=k,
            min_score=0.0,
        )
        return [
            result.document.metadata["source"]
            for result in results
        ]

    for k in (1, 3):
        metrics = evaluate_retriever(
            cases=EVALUATION_CASES,
            retrieve_sources=retrieve_ngram_sources,
            k=k,
        )
        print(
            f"\nn-gram @ {k}："
            f"Recall={metrics.recall_at_k:.1%}，"
            f"Precision={metrics.precision_at_k:.1%}，"
            f"平均耗时={metrics.average_latency_ms:.3f}ms\n"
        )


if __name__ == "__main__":
    main()
