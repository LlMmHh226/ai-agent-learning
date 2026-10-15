# 课程：step_17b_dense_score_eval.md；访问范围：真实外部请求（可能收费）。
from dataclasses import dataclass

from app.rag.chunker import split_documents
from app.rag.dense_retriever import calculate_cosine_similarity
from app.rag.document_loader import Document, load_markdown_documents
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError
from learning.rag.step_16h_01_ngram_eval_baseline import EVALUATION_CASES
from learning.rag.step_17a_no_answer_eval import NO_ANSWER_CASES


@dataclass(frozen=True)
class DenseScoreCase:
    question: str
    expected_source: str | None


@dataclass(frozen=True)
class DenseScoreObservation:
    question: str
    expected_source: str | None
    top_source: str
    top_score: float


@dataclass(frozen=True)
class DenseScoreBoundary:
    minimum_positive_score: float
    maximum_negative_score: float
    candidate_threshold: float | None


SCORE_CASES = [
    *[
        DenseScoreCase(
            question=case.question,
            expected_source=case.expected_source,
        )
        for case in EVALUATION_CASES
    ],
    *[
        DenseScoreCase(
            question=case.question,
            expected_source=None,
        )
        for case in NO_ANSWER_CASES
    ],
]


def build_observations(
    cases: list[DenseScoreCase],
    query_vectors: list[list[float]],
    documents: list[Document],
    document_vectors: list[list[float]],
) -> list[DenseScoreObservation]:
    """计算每个问题的 Dense Top-1 来源与分数。"""
    if len(cases) != len(query_vectors):
        raise ValueError("问题数量与 query 向量数量不一致")
    if len(documents) != len(document_vectors):
        raise ValueError("文档数量与 document 向量数量不一致")
    if not documents:
        raise ValueError("候选文档不能为空")

    observations: list[DenseScoreObservation] = []
    for case, query_vector in zip(cases, query_vectors):
        ranked_documents = sorted(
            (
                (
                    document,
                    calculate_cosine_similarity(
                        vector_a=query_vector,
                        vector_b=document_vector,
                    ),
                )
                for document, document_vector in zip(
                    documents,
                    document_vectors,
                )
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        top_document, top_score = ranked_documents[0]
        observations.append(
            DenseScoreObservation(
                question=case.question,
                expected_source=case.expected_source,
                top_source=top_document.metadata["source"],
                top_score=top_score,
            )
        )

    return observations


def analyze_score_boundary(
    observations: list[DenseScoreObservation],
) -> DenseScoreBoundary:
    """检查正例最低分与负例最高分之间是否存在无重叠区间。"""
    positive_scores = [
        observation.top_score
        for observation in observations
        if observation.expected_source is not None
        and observation.top_source == observation.expected_source
    ]
    negative_scores = [
        observation.top_score
        for observation in observations
        if observation.expected_source is None
    ]

    if not positive_scores:
        raise ValueError("没有 Top-1 来源正确的正例")
    if not negative_scores:
        raise ValueError("没有无答案负例")

    minimum_positive_score = min(positive_scores)
    maximum_negative_score = max(negative_scores)
    candidate_threshold = None
    if maximum_negative_score < minimum_positive_score:
        candidate_threshold = (
            maximum_negative_score + minimum_positive_score
        ) / 2

    return DenseScoreBoundary(
        minimum_positive_score=minimum_positive_score,
        maximum_negative_score=maximum_negative_score,
        candidate_threshold=candidate_threshold,
    )


def main() -> None:
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
            [case.question for case in SCORE_CASES]
        )
    except EmbeddingServiceError as error:
        print(f"Dense 分数评测停止：{error}")
        raise SystemExit(1) from error

    observations = build_observations(
        cases=SCORE_CASES,
        query_vectors=query_vectors,
        documents=documents,
        document_vectors=document_vectors,
    )

    for observation in observations:
        label = (
            f"正例 expected={observation.expected_source}"
            if observation.expected_source is not None
            else "负例 expected=拒答"
        )
        print(
            f"{label:31} "
            f"top1={observation.top_source:14} "
            f"score={observation.top_score:.4f} "
            f"问题={observation.question}"
        )

    boundary = analyze_score_boundary(observations)
    print(f"\n正确正例最低 Top-1 分数：{boundary.minimum_positive_score:.4f}")
    print(f"无答案负例最高 Top-1 分数：{boundary.maximum_negative_score:.4f}")
    if boundary.candidate_threshold is None:
        print("正负例分数发生重叠：当前样本中不存在可完美分开的单一阈值。")
    else:
        print(
            f"当前样本存在分数间隔，候选阈值："
            f"{boundary.candidate_threshold:.4f}"
        )
        print("该数值只用于当前小样本观察，不直接写入正式配置。")


if __name__ == "__main__":
    main()
