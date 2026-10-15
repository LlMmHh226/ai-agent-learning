# 课程：step_17a_no_answer_eval.md；访问范围：本地运行（无外部模型请求）。
from collections.abc import Callable
from dataclasses import dataclass

from app.rag.retriever import retrieve


@dataclass(frozen=True)
class NoAnswerEvalCase:
    question: str
    missing_fact: str


@dataclass(frozen=True)
class NoAnswerEvalMetrics:
    correctly_rejected: int
    total: int

    @property
    def refusal_rate(self) -> float:
        return self.correctly_rejected / self.total


NO_ANSWER_CASES = [
    NoAnswerEvalCase(
        question="商品有优惠券吗？",
        missing_fact="知识库没有优惠券规则",
    ),
    NoAnswerEvalCase(
        question="能开增值税专用发票吗？",
        missing_fact="知识库没有发票政策",
    ),
    NoAnswerEvalCase(
        question="下单后能修改收货地址吗？",
        missing_fact="知识库没有修改收货地址流程",
    ),
    NoAnswerEvalCase(
        question="退货运费谁承担？",
        missing_fact="知识库只写了质量问题换货运费，没有说明退货运费",
    ),
    NoAnswerEvalCase(
        question="轻风无线鼠标的电池能单独更换吗？",
        missing_fact="知识库只写了充电与续航，没有说明电池能否更换",
    ),
]


def evaluate_no_answer_cases(
    cases: list[NoAnswerEvalCase],
    retrieve_sources: Callable[[str], list[str]],
) -> NoAnswerEvalMetrics:
    """统计无答案问题中，检索器返回空候选的比例。"""
    if not cases:
        raise ValueError("无答案评测用例不能为空")

    correctly_rejected = 0
    for case in cases:
        returned_sources = retrieve_sources(case.question)
        rejected = not returned_sources
        if rejected:
            correctly_rejected += 1

        print(
            f"拒答={rejected!s:5} "
            f"返回={returned_sources} "
            f"问题={case.question} "
            f"标注原因={case.missing_fact}"
        )

    return NoAnswerEvalMetrics(
        correctly_rejected=correctly_rejected,
        total=len(cases),
    )


def main() -> None:
    # 正式 RAGService 的 chunk、Top-K 和阈值，确保本次观察与正式配置一致。
    from app.services.rag_service import rag_service

    def retrieve_formal_sources(question: str) -> list[str]:
        results = retrieve(
            query=question,
            chunks=rag_service.chunks,
            top_k=rag_service.top_k,
            min_score=rag_service.min_score,
        )
        return [result.document.metadata["source"] for result in results]

    metrics = evaluate_no_answer_cases(
        cases=NO_ANSWER_CASES,
        retrieve_sources=retrieve_formal_sources,
    )
    print(
        f"\n程序级拒答触发率："
        f"{metrics.correctly_rejected}/{metrics.total} "
        f"= {metrics.refusal_rate:.1%}"
    )


if __name__ == "__main__":
    main()
