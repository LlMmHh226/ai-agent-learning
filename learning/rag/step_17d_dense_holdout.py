# 课程：step_17d_dense_holdout.md；访问范围：真实外部请求（可能收费）。
from dataclasses import dataclass

from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError
from learning.rag.step_17b_dense_score_eval import (
    SCORE_CASES,
    DenseScoreCase,
    DenseScoreObservation,
    build_observations,
)
from learning.rag.step_17c_02_holdout_eval import (
    HOLDOUT_CASES,
    validate_holdout_cases,
)


# 这些值来自 17C-1 的开发题比较，在看新题的 Dense 分数之前固定。
FIXED_THRESHOLDS = (0.30, 0.40, 0.46)


@dataclass(frozen=True)
class DenseHoldoutMetrics:
    threshold: float
    positive_correct: int
    positive_rejected: int
    positive_wrong_source: int
    negative_rejected: int
    negative_passed: int


def evaluate_fixed_threshold(
    observations: list[DenseScoreObservation],
    threshold: float,
) -> DenseHoldoutMetrics:
    """区分正例命中、正例误拒、来源错排和负例放行。"""
    if not observations:
        raise ValueError("留出评测观察值不能为空")

    positive_correct = 0
    positive_rejected = 0
    positive_wrong_source = 0
    negative_rejected = 0
    negative_passed = 0

    for observation in observations:
        passed = observation.top_score >= threshold

        if observation.expected_source is None:
            if passed:
                negative_passed += 1
            else:
                negative_rejected += 1
        elif not passed:
            positive_rejected += 1
        elif observation.top_source == observation.expected_source:
            positive_correct += 1
        else:
            positive_wrong_source += 1

    return DenseHoldoutMetrics(
        threshold=threshold,
        positive_correct=positive_correct,
        positive_rejected=positive_rejected,
        positive_wrong_source=positive_wrong_source,
        negative_rejected=negative_rejected,
        negative_passed=negative_passed,
    )


def main() -> None:
    validate_holdout_cases(
        cases=HOLDOUT_CASES,
        used_questions={case.question for case in SCORE_CASES},
    )
    score_cases = [
        DenseScoreCase(
            question=case.question,
            expected_source=case.expected_source,
        )
        for case in HOLDOUT_CASES
    ]
    documents = split_documents(
        documents=load_markdown_documents(),
        chunk_size=10_000,
        overlap=0,
    )
    embedding_service = EmbeddingService()

    try:
        document_vectors = embedding_service.embed_documents(
            [document.content for document in documents]
        )
        query_vectors = embedding_service.embed_queries(
            [case.question for case in score_cases]
        )
    except EmbeddingServiceError as error:
        print(f"Dense 留出评测停止：{error}")
        raise SystemExit(1) from error

    observations = build_observations(
        cases=score_cases,
        query_vectors=query_vectors,
        documents=documents,
        document_vectors=document_vectors,
    )

    for observation in observations:
        expected = observation.expected_source or "拒答"
        print(
            f"预期={expected:14} "
            f"Top-1={observation.top_source:14} "
            f"分数={observation.top_score:.4f} "
            f"问题={observation.question}"
        )

    print("\n固定候选阈值在新题上的结果：")
    for threshold in FIXED_THRESHOLDS:
        metrics = evaluate_fixed_threshold(observations, threshold)
        print(
            f"阈值={metrics.threshold:.2f} "
            f"正例正确={metrics.positive_correct}/5 "
            f"正例误拒={metrics.positive_rejected}/5 "
            f"正例来源错排={metrics.positive_wrong_source}/5 "
            f"负例拒答={metrics.negative_rejected}/5 "
            f"负例误放={metrics.negative_passed}/5"
        )


if __name__ == "__main__":
    main()
