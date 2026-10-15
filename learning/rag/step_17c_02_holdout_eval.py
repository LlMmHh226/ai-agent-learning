# 课程：step_17c_02_holdout_eval.md；访问范围：本地运行（无外部模型请求）。
from collections.abc import Callable
from dataclasses import dataclass

from app.rag.retriever import retrieve
from learning.rag.step_17b_dense_score_eval import SCORE_CASES


@dataclass(frozen=True)
class HoldoutCase:
    question: str
    expected_source: str | None
    label_reason: str


@dataclass(frozen=True)
class HoldoutMetrics:
    positive_correct: int
    positive_total: int
    negative_correct: int
    negative_total: int


HOLDOUT_CASES = [
    HoldoutCase(
        "星云机械键盘换轴需要焊接吗？",
        "products.md",
        "文档说明更换轴体不需要焊接",
    ),
    HoldoutCase(
        "轻风无线鼠标支持 2.4 GHz 接收器连接吗？",
        "products.md",
        "文档说明支持 2.4 GHz 接收器",
    ),
    HoldoutCase(
        "预售商品按什么时候发货？",
        "shipping.md",
        "文档说明按商品页面标注日期发货",
    ),
    HoldoutCase(
        "退货申请要在哪里提交？",
        "after_sales.md",
        "文档说明在订单详情页提交申请",
    ),
    HoldoutCase(
        "退款会退回原来的支付渠道吗？",
        "after_sales.md",
        "文档说明验收通过后原路退回",
    ),
    HoldoutCase(
        "星云机械键盘能同时连接几台设备？",
        None,
        "文档只列出连接方式，没有同时连接设备数量",
    ),
    HoldoutCase(
        "鼠标充电时还能继续使用吗？",
        None,
        "文档说明可充电，没有边充边用规则",
    ),
    HoldoutCase(
        "预售商品可以加钱提前发货吗？",
        None,
        "文档说明按页面日期发货，没有加钱提前发货规则",
    ),
    HoldoutCase(
        "订单支持货到付款吗？",
        None,
        "文档没有货到付款政策",
    ),
    HoldoutCase(
        "物流由哪家快递公司配送？",
        None,
        "文档没有指定快递公司",
    ),
]


def validate_holdout_cases(
    cases: list[HoldoutCase],
    used_questions: set[str],
) -> None:
    """确保留出题非空、不重复，且没有用过完全相同的问题。"""
    if not cases:
        raise ValueError("留出评测集不能为空")

    questions = [case.question.strip() for case in cases]
    if len(set(questions)) != len(questions):
        raise ValueError("留出评测集包含重复问题")
    if set(questions) & used_questions:
        raise ValueError("留出题与已用于观察分数的问题重复")


def evaluate_holdout(
    cases: list[HoldoutCase],
    retrieve_sources: Callable[[str], list[str]],
) -> HoldoutMetrics:
    """分别统计有答案题来源命中数和无答案题空结果数。"""
    if not cases:
        raise ValueError("留出评测集不能为空")

    positive_correct = 0
    positive_total = 0
    negative_correct = 0
    negative_total = 0

    for case in cases:
        returned_sources = retrieve_sources(case.question)
        if case.expected_source is None:
            negative_total += 1
            correct = not returned_sources
            if correct:
                negative_correct += 1
        else:
            positive_total += 1
            correct = case.expected_source in returned_sources
            if correct:
                positive_correct += 1

        print(
            f"正确={correct!s:5} "
            f"预期={case.expected_source or '拒答':14} "
            f"返回={returned_sources} "
            f"问题={case.question}"
        )

    return HoldoutMetrics(
        positive_correct=positive_correct,
        positive_total=positive_total,
        negative_correct=negative_correct,
        negative_total=negative_total,
    )


def main() -> None:
    used_questions = {case.question for case in SCORE_CASES}
    validate_holdout_cases(HOLDOUT_CASES, used_questions)

    from app.services.rag_service import rag_service

    def retrieve_formal_sources(question: str) -> list[str]:
        results = retrieve(
            query=question,
            chunks=rag_service.chunks,
            top_k=rag_service.top_k,
            min_score=rag_service.min_score,
        )
        return [result.document.metadata["source"] for result in results]

    metrics = evaluate_holdout(
        cases=HOLDOUT_CASES,
        retrieve_sources=retrieve_formal_sources,
    )
    print(
        f"\n正式 n-gram 留出题："
        f"有答案来源命中 {metrics.positive_correct}/{metrics.positive_total}；"
        f"无答案空结果 {metrics.negative_correct}/{metrics.negative_total}"
    )


if __name__ == "__main__":
    main()
